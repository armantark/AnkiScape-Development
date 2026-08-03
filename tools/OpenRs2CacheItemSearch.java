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
            System.err.println("   or: OpenRs2CacheItemSearch <cache-dir> --id <id> [id ...]");
            System.exit(2);
        }

        String cacheDirectory = args[0].endsWith(File.separator) ? args[0] : args[0] + File.separator;
        Store store = new Store(cacheDirectory, false);
        Cache.STORE = store;
        if (args[1].equals("--id")) {
            for (int i = 2; i < args.length; i++) {
                printExactDefinition(store, Integer.parseInt(args[i]));
            }
            return;
        }
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

    private static void printExactDefinition(Store store, int id) {
        ItemDefinitions definition = ItemDefinitions.getItemDefinitions(store, id);
        System.out.printf(
                "%d\t%s\tmodel=%d\trecolors=%s->%s\ttextures=%s->%s\tsprite-recolors=%s\tbonuses=%s\tstackable=%s\texchangeable=%s\toptions=%s%n",
                id,
                definition.name,
                definition.modelId,
                Arrays.toString(definition.originalModelColors),
                Arrays.toString(definition.modifiedModelColors),
                Arrays.toString(definition.originalTextureIds),
                Arrays.toString(definition.modifiedTextureIds),
                Arrays.toString(definition.spriteRecolorIndices),
                Arrays.toString(definition.bonuses),
                definition.isStackable(),
                definition.canExchange(),
                Arrays.toString(definition.inventoryOptions));
    }
}
