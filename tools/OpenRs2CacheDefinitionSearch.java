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
            System.err.println("usage: OpenRs2CacheDefinitionSearch <cache-dir> <npc|object> <term> [term ...]");
            System.err.println("   or: OpenRs2CacheDefinitionSearch <cache-dir> <npc|object> --id <id> [id ...]");
            System.err.println("   or: OpenRs2CacheDefinitionSearch <cache-dir> <npc|object> --params <id> [id ...]");
            System.err.println("   or: OpenRs2CacheDefinitionSearch <cache-dir> npc --combat-levels <id> [id ...]");
            System.exit(2);
        }

        String cacheDirectory = args[0].endsWith(File.separator) ? args[0] : args[0] + File.separator;
        Store store = new Store(cacheDirectory, false);
        Cache.STORE = store;
        String kind = args[1].toLowerCase(Locale.ROOT);
        if (args[2].equals("--id")) {
            for (int i = 3; i < args.length; i++) {
                int id = Integer.parseInt(args[i]);
                if (kind.equals("npc")) {
                    NPCDefinitions definition = NPCDefinitions.getDefs(id);
                    System.out.printf("%d\t%s\t%s%n", id, definition == null ? null : definition.getName(), definition == null ? null : Arrays.toString(definition.options));
                } else if (kind.equals("object")) {
                    ObjectDefinitions definition = ObjectDefinitions.getDefs(id);
                    System.out.printf("%d\t%s\t%s%n", id, definition == null ? null : definition.getName(), definition == null ? null : Arrays.toString(definition.options));
                } else {
                    System.err.println("entity kind must be npc or object");
                    System.exit(2);
                }
            }
            return;
        }
        if (args[2].equals("--params")) {
            for (int i = 3; i < args.length; i++) {
                int id = Integer.parseInt(args[i]);
                if (kind.equals("npc")) {
                    NPCDefinitions definition = NPCDefinitions.getDefs(id);
                    System.out.printf("%d\t%s\t%s%n", id, definition == null ? null : definition.getName(), sortedParameters(definition == null ? null : definition.parameters));
                } else if (kind.equals("object")) {
                    ObjectDefinitions definition = ObjectDefinitions.getDefs(id);
                    System.out.printf("%d\t%s\t%s%n", id, definition == null ? null : definition.getName(), sortedParameters(definition == null ? null : definition.parameters));
                } else {
                    System.err.println("entity kind must be npc or object");
                    System.exit(2);
                }
            }
            return;
        }
        if (args[2].equals("--combat-levels")) {
            if (!kind.equals("npc")) {
                System.err.println("combat levels are available only for NPC definitions");
                System.exit(2);
            }
            for (int i = 3; i < args.length; i++) {
                int id = Integer.parseInt(args[i]);
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

        Index index = kind.equals("npc")
                ? store.getIndex(IndexType.NPCS)
                : kind.equals("object") ? store.getIndex(IndexType.OBJECTS) : null;
        int filesPerArchive = kind.equals("npc") ? 128 : 256;
        int maxId = index == null
                ? -1
                : index.getLastArchiveId() * filesPerArchive
                        + index.getLastFileId(index.getLastArchiveId()) + 1;
        if (maxId < 0) {
            System.err.println("entity kind must be npc or object");
            System.exit(2);
        }

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

    private static Map<Integer, Object> sortedParameters(Map<Integer, Object> parameters) {
        return parameters == null ? Map.of() : new TreeMap<>(parameters);
    }
}
