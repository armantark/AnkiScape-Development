import com.rs.cache.Cache;
import com.rs.cache.loaders.ItemDefinitions;

import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;

/**
 * Dumps every item's name, store value, and stackable flag from the Darkan cache
 * so AnkiScape can value combat drops (which are keyed by name) for the loot
 * filter. Complements DumpDarkanShopPriceInputs, which is keyed by a fixed id set.
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
        Cache.init(args[0]);
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
                    .append("\"stackable\":").append(defs.stackable)
                    .append("}");
        }
        json.append("\n  }\n}\n");
        Files.writeString(Path.of(args[2]), json.toString(), StandardCharsets.UTF_8);
    }

    private static String jsonEscape(String value) {
        return value.replace("\\", "\\\\").replace("\"", "\\\"");
    }
}
