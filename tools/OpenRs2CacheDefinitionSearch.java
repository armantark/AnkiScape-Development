import com.rs.cache.Cache;
import com.rs.cache.Index;
import com.rs.cache.IndexType;
import com.rs.cache.Store;
import com.rs.cache.loaders.NPCDefinitions;
import com.rs.cache.loaders.ObjectDefinitions;

import java.io.File;
import java.nio.BufferUnderflowException;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.List;
import java.util.Locale;
import java.util.Map;
import java.util.TreeMap;

/** Read-only name/option search for dated OpenRS2 NPC and object definitions. */
final class OpenRs2CacheDefinitionSearch {
    private OpenRs2CacheDefinitionSearch() {}

    public static void main(String[] args) throws Exception {
        if (args.length < 3) {
            usage("cache path, entity kind and query are required");
        }
        String kind = args[1].toLowerCase(Locale.ROOT);
        if (!kind.equals("npc") && !kind.equals("object")) {
            usage("entity kind must be npc or object");
        }
        int[] ids = parseDefinitionIds(args, kind);
        String cacheDirectory = args[0].endsWith(File.separator) ? args[0] : args[0] + File.separator;
        Store store = new Store(cacheDirectory, false);
        Cache.STORE = store;
        if (args[2].equals("--id")) {
            for (int id : ids) {
                if (kind.equals("npc")) {
                    NPCDefinitions definition = NPCDefinitions.getDefs(id);
                    System.out.printf("%d\t%s\t%s%n", id, definition == null ? null : definition.getName(), definition == null ? null : Arrays.toString(definition.options));
                } else {
                    ObjectDefinitions definition = ObjectDefinitions.getDefs(id);
                    System.out.printf("%d\t%s\t%s%n", id, definition == null ? null : definition.getName(), definition == null ? null : Arrays.toString(definition.options));
                }
            }
            return;
        }
        if (args[2].equals("--params")) {
            for (int id : ids) {
                if (kind.equals("npc")) {
                    NPCDefinitions definition = NPCDefinitions.getDefs(id);
                    System.out.printf("%d\t%s\t%s%n", id, definition == null ? null : definition.getName(), sortedParameters(definition == null ? null : definition.parameters));
                } else {
                    ObjectDefinitions definition = ObjectDefinitions.getDefs(id);
                    System.out.printf("%d\t%s\t%s%n", id, definition == null ? null : definition.getName(), sortedParameters(definition == null ? null : definition.parameters));
                }
            }
            return;
        }
        if (args[2].equals("--combat-levels")) {
            for (int id : ids) {
                NPCDefinitions definition = NPCDefinitions.getDefs(id);
                System.out.printf(
                        "%d\t%s\t%d%n",
                        id,
                        definition == null ? null : definition.getName(),
                        definition == null ? -1 : definition.combatLevel);
            }
            return;
        }
        String[] terms = Arrays.stream(args, 2, args.length)
                .map(value -> value.toLowerCase(Locale.ROOT))
                .toArray(String[]::new);

        IndexType indexType = kind.equals("npc") ? IndexType.NPCS : IndexType.OBJECTS;
        int indexId = indexType.getId();
        Index[] indexes = store.getIndices();
        Index index = indexId < indexes.length ? indexes[indexId] : null;
        if (index == null) {
            System.err.println("cache is missing the " + indexType + " index");
            System.exit(1);
        }
        int filesPerArchive = kind.equals("npc") ? 128 : 256;
        int maxId = index.getLastArchiveId() * filesPerArchive
                + index.getLastFileId(index.getLastArchiveId()) + 1;

        List<Integer> skippedIds = new ArrayList<>();
        for (int id = 0; id < maxId; id++) {
            String name;
            String[] options;
            try {
                if (kind.equals("npc")) {
                    NPCDefinitions definition = NPCDefinitions.getDefs(id);
                    if (definition == null) continue;
                    name = definition.getName();
                    options = definition.options;
                } else {
                    ObjectDefinitions definition = ObjectDefinitions.getDefs(id);
                    if (definition == null) continue;
                    name = definition.getName();
                    options = definition.options;
                }
            } catch (BufferUnderflowException ignored) {
                skippedIds.add(id);
                continue;
            }
            if (name == null) continue;
            String haystack = name.toLowerCase(Locale.ROOT);
            if (Arrays.stream(terms).noneMatch(haystack::contains)) continue;
            System.out.printf("%d\t%s\t%s%n", id, name, Arrays.toString(options));
        }
        if (!skippedIds.isEmpty()) {
            System.err.printf(
                    "PARTIAL_SEARCH skipped_count=%d skipped_ids=%s%n",
                    skippedIds.size(), skippedIds
            );
            System.exit(3);
        }
    }

    private static int[] parseDefinitionIds(String[] args, String kind) {
        int[] ids = new int[0];
        if (args[2].equals("--id") || args[2].equals("--params") || args[2].equals("--combat-levels")) {
            if (args.length == 3) {
                usage(args[2] + " requires at least one ID");
            }
            if (args[2].equals("--combat-levels") && !kind.equals("npc")) {
                usage("combat levels are available only for NPC definitions");
            }
            ids = new int[args.length - 3];
            for (int i = 3; i < args.length; i++) {
                if (!args[i].matches("\\+?[0-9]+")) {
                    usage("invalid definition ID: " + args[i]);
                }
                try {
                    ids[i - 3] = Integer.parseInt(args[i]);
                } catch (NumberFormatException invalidId) {
                    usage("definition ID out of range: " + args[i]);
                }
            }
        }
        return ids;
    }

    private static void usage(String diagnostic) {
        System.err.println(diagnostic);
        System.err.println("usage: OpenRs2CacheDefinitionSearch <cache-dir> <npc|object> <term> [term ...]");
        System.err.println("   or: OpenRs2CacheDefinitionSearch <cache-dir> <npc|object> --id <id> [id ...]");
        System.err.println("   or: OpenRs2CacheDefinitionSearch <cache-dir> <npc|object> --params <id> [id ...]");
        System.err.println("   or: OpenRs2CacheDefinitionSearch <cache-dir> npc --combat-levels <id> [id ...]");
        System.exit(2);
    }

    private static Map<Integer, Object> sortedParameters(Map<Integer, Object> parameters) {
        return parameters == null ? Map.of() : new TreeMap<>(parameters);
    }
}
