import com.rs.cache.Cache;
import com.rs.cache.Store;
import com.rs.cache.loaders.ItemDefinitions;

import java.util.Arrays;
import java.util.Locale;
import java.io.File;

final class OpenRs2CacheItemSearch {
    private static final int MAX_ITEM_ID = 40_000;

    private OpenRs2CacheItemSearch() {}

    public static void main(String[] args) throws Exception {
        if (args.length < 2) {
            System.err.println("usage: OpenRs2CacheItemSearch <cache-dir> <term> [term ...]");
            System.exit(2);
        }

        String cacheDirectory = args[0].endsWith(File.separator) ? args[0] : args[0] + File.separator;
        Store store = new Store(cacheDirectory, false);
        Cache.STORE = store;
        String[] terms = Arrays.stream(args, 1, args.length)
                .map(value -> value.toLowerCase(Locale.ROOT))
                .toArray(String[]::new);

        for (int id = 0; id < MAX_ITEM_ID; id++) {
            ItemDefinitions definition;
            try {
                definition = ItemDefinitions.getItemDefinitions(store, id);
            } catch (RuntimeException ignored) {
                continue;
            }
            if (definition == null || definition.name == null) {
                continue;
            }
            String name = definition.name.toLowerCase(Locale.ROOT);
            if (Arrays.stream(terms).noneMatch(name::contains)) {
                continue;
            }
            System.out.printf("%d\t%s\t%s%n", id, definition.name, Arrays.toString(definition.inventoryOptions));
        }
    }
}
