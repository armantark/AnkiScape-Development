import com.rs.cache.Cache;
import com.rs.cache.Index;
import com.rs.cache.MainFile;
import com.rs.cache.Store;
import com.rs.cache.loaders.ItemDefinitions;
import sun.misc.Unsafe;

import java.io.RandomAccessFile;
import java.lang.reflect.Constructor;
import java.lang.reflect.Field;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;

/**
 * Dumps every item's name, store value, stackable flag, and Grand Exchange
 * eligibility from the Darkan cache. AnkiScape consumes the name-keyed output
 * for loot valuation, carried slots, and its local Grand Exchange catalog.
 *
 * usage: DumpDarkanItemValues &lt;cache-path&gt; &lt;max-id&gt; &lt;output-json&gt;
 */
public final class DumpDarkanItemValues {
    private DumpDarkanItemValues() {
    }

    public static void main(String[] args) throws Exception {
        if (args.length != 3) {
            throw new IllegalArgumentException("usage: DumpDarkanItemValues <cache-path> <max-id> <output-json>");
        }
        Cache.STORE = openItemStore(args[0]);
        int maxId = Integer.parseInt(args[1]);

        StringBuilder json = new StringBuilder();
        json.append("{\n  \"items\": {\n");
        boolean first = true;
        for (int itemId = 0; itemId <= maxId; itemId++) {
            ItemDefinitions defs;
            try {
                defs = ItemDefinitions.getDefs(itemId);
            } catch (Throwable error) {
                continue;
            }
            if (defs == null) {
                continue;
            }
            // Skip noted variants: they share the real item's name but are always
            // stackable, which would pollute the stackable set.
            if (defs.noted) {
                continue;
            }
            String name = defs.getName();
            if (name == null || name.isEmpty() || "null".equals(name)) {
                continue;
            }
            if (!first) {
                json.append(",\n");
            }
            first = false;
            json.append("    \"").append(itemId).append("\": {")
                    .append("\"name\":\"").append(jsonEscape(name)).append("\",")
                    .append("\"value\":").append(defs.getValue()).append(',')
                    .append("\"stackable\":").append(defs.stackable).append(',')
                    .append("\"exchangeable\":").append(defs.canExchange())
                    .append("}");
        }
        json.append("\n  }\n}\n");
        Files.writeString(Path.of(args[2]), json.toString(), StandardCharsets.UTF_8);
    }

    /**
     * The source cache intentionally has an empty Huffman index. Darkan's full
     * Store constructor eagerly opens Huffman even though item definitions only
     * need index 19, so build the same read-only store boundary without that
     * unrelated index.
     */
    private static Store openItemStore(String cachePath) throws Exception {
        Field unsafeField = Unsafe.class.getDeclaredField("theUnsafe");
        unsafeField.setAccessible(true);
        Unsafe unsafe = (Unsafe) unsafeField.get(null);
        Store store = (Store) unsafe.allocateInstance(Store.class);

        Path root = Path.of(cachePath);
        RandomAccessFile data = new RandomAccessFile(root.resolve("main_file_cache.dat2").toFile(), "r");
        Constructor<MainFile> mainFileConstructor = MainFile.class.getDeclaredConstructor(
                int.class,
                RandomAccessFile.class,
                RandomAccessFile.class,
                boolean.class
        );
        mainFileConstructor.setAccessible(true);
        MainFile index255 = mainFileConstructor.newInstance(
                255,
                data,
                new RandomAccessFile(root.resolve("main_file_cache.idx255").toFile(), "r"),
                false
        );
        int itemIndexId = 19;
        Index[] indexes = new Index[Math.max(index255.getArchivesCount(), itemIndexId + 1)];
        MainFile itemMainFile = mainFileConstructor.newInstance(
                itemIndexId,
                data,
                new RandomAccessFile(root.resolve("main_file_cache.idx" + itemIndexId).toFile(), "r"),
                false
        );
        Constructor<Index> indexConstructor = Index.class.getDeclaredConstructor(
                MainFile.class,
                MainFile.class,
                boolean.class
        );
        indexConstructor.setAccessible(true);
        indexes[itemIndexId] = indexConstructor.newInstance(index255, itemMainFile, false);

        setField(store, "path", cachePath);
        setField(store, "data", data);
        setField(store, "index255", index255);
        setField(store, "indexes", indexes);
        return store;
    }

    private static void setField(Object target, String name, Object value) throws Exception {
        Field field = target.getClass().getDeclaredField(name);
        field.setAccessible(true);
        field.set(target, value);
    }

    private static String jsonEscape(String value) {
        return value.replace("\\", "\\\\").replace("\"", "\\\"");
    }
}
