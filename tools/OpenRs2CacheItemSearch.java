import com.rs.cache.Cache;
import com.rs.cache.Index;
import com.rs.cache.IndexType;
import com.rs.cache.Store;
import com.rs.cache.loaders.ItemDefinitions;

import java.nio.BufferUnderflowException;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.List;
import java.util.Locale;
import java.io.File;

final class OpenRs2CacheItemSearch {
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

        Index index = store.getIndex(IndexType.ITEMS);
        int lastArchiveId = index.getLastArchiveId();
        int maxId = lastArchiveId * 256 + index.getLastFileId(lastArchiveId) + 1;
        List<Integer> skippedIds = new ArrayList<>();
        for (int id = 0; id < maxId; id++) {
            ItemDefinitions definition;
            try {
                definition = ItemDefinitions.getItemDefinitions(store, id);
            } catch (RuntimeException error) {
                boolean missingOpcode = error.getMessage() != null
                        && error.getMessage().startsWith("MISSING OPCODE ");
                boolean truncatedDefinition = error instanceof BufferUnderflowException;
                boolean invalidParamType = error instanceof ClassCastException
                        && (error.getStackTrace().length == 0
                                || error.getStackTrace()[0].getClassName()
                                        .equals(ItemDefinitions.class.getName()));
                if (!missingOpcode && !truncatedDefinition && !invalidParamType) {
                    throw error;
                }
                skippedIds.add(id);
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
        if (!skippedIds.isEmpty()) {
            System.err.printf(
                    "PARTIAL_SEARCH skipped_count=%d skipped_ids=%s%n",
                    skippedIds.size(), skippedIds
            );
            System.exit(3);
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
