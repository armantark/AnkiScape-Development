import com.rs.cache.ArchiveType;
import com.rs.cache.Cache;
import com.rs.cache.Index;
import com.rs.cache.IndexType;
import com.rs.cache.Store;
import com.rs.cache.loaders.EnumDefinitions;
import com.rs.cache.loaders.StructDefinitions;
import com.rs.lib.io.InputStream;

import java.io.File;
import java.util.ArrayList;
import java.util.Comparator;
import java.util.List;
import java.util.Locale;
import java.util.Map;

/** Read-only query tool for enum, struct, and param definitions in a disk cache. */
final class OpenRs2CacheConfigQuery {
    private OpenRs2CacheConfigQuery() {}

    private enum Kind {
        ENUM,
        STRUCT,
        PARAM;

        static Kind parse(String value) {
            return switch (value.toLowerCase(Locale.ROOT)) {
                case "enum" -> ENUM;
                case "struct" -> STRUCT;
                case "param" -> PARAM;
                default -> throw new IllegalArgumentException(
                        "definition kind must be enum, struct, or param"
                );
            };
        }
    }

    private record ParamDefinition(
            char type,
            int defaultInt,
            String defaultString,
            boolean autoDisable
    ) {}

    public static void main(String[] args) throws Exception {
        if (args.length < 3) {
            usage();
            System.exit(2);
        }

        String cacheDirectory = args[0].endsWith(File.separator)
                ? args[0]
                : args[0] + File.separator;
        Store store = new Store(cacheDirectory, false);
        Cache.STORE = store;
        Kind kind = Kind.parse(args[1]);
        String mode = args[2].toLowerCase(Locale.ROOT);
        List<Integer> ids = existingIds(store, kind);

        switch (mode) {
            case "count" -> printCount(store, kind, ids);
            case "dump" -> {
                if (args.length < 4) {
                    usage();
                    System.exit(2);
                }
                for (int index = 3; index < args.length; index++) {
                    int id = Integer.parseInt(args[index]);
                    if (!ids.contains(id)) {
                        System.out.printf("==== %s %d absent%n", label(kind), id);
                        continue;
                    }
                    System.out.print(render(store, kind, id));
                }
            }
            case "find" -> {
                if (args.length != 4) {
                    usage();
                    System.exit(2);
                }
                String needle = args[3].toLowerCase(Locale.ROOT);
                for (int id : ids) {
                    String rendered = render(store, kind, id);
                    if (rendered.toLowerCase(Locale.ROOT).contains(needle)) {
                        System.out.print(rendered);
                    }
                }
            }
            default -> {
                usage();
                System.exit(2);
            }
        }
    }

    private static void usage() {
        System.err.println(
                "usage: OpenRs2CacheConfigQuery <cache-dir> "
                        + "<enum|struct|param> <count|dump|find> [id ...|needle]"
        );
    }

    private static String label(Kind kind) {
        return kind.name().toLowerCase(Locale.ROOT);
    }

    private static List<Integer> existingIds(Store store, Kind kind) {
        Index index = store.getIndex(kind == Kind.ENUM ? IndexType.ENUMS : IndexType.CONFIG);
        ArchiveType archiveType = switch (kind) {
            case ENUM -> ArchiveType.ENUMS;
            case STRUCT -> ArchiveType.STRUCTS;
            case PARAM -> ArchiveType.PARAMS;
        };
        List<Integer> ids = new ArrayList<>();
        if (kind == Kind.ENUM) {
            for (int archive = 0; archive <= index.getLastArchiveId(); archive++) {
                if (!index.archiveExists(archive)) {
                    continue;
                }
                for (int file = 0; file <= index.getLastFileId(archive); file++) {
                    if (index.fileExists(archive, file)) {
                        ids.add(archive * archiveType.filesPerContainer() + file);
                    }
                }
            }
        } else {
            int archive = archiveType.getId();
            if (index.archiveExists(archive)) {
                for (int file = 0; file <= index.getLastFileId(archive); file++) {
                    if (index.fileExists(archive, file)) {
                        ids.add(file);
                    }
                }
            }
        }
        return ids;
    }

    private static void printCount(Store store, Kind kind, List<Integer> ids) {
        int indexId = store.getIndex(kind == Kind.ENUM ? IndexType.ENUMS : IndexType.CONFIG).getId();
        int first = ids.isEmpty() ? -1 : ids.getFirst();
        int last = ids.isEmpty() ? -1 : ids.getLast();
        System.out.printf(
                "kind=%s index=%d definitions=%d firstId=%d lastId=%d%n",
                label(kind), indexId, ids.size(), first, last
        );
    }

    private static String render(Store store, Kind kind, int id) {
        return switch (kind) {
            case ENUM -> renderEnum(id);
            case STRUCT -> renderStruct(id);
            case PARAM -> renderParam(store, id);
        };
    }

    private static String renderEnum(int id) {
        EnumDefinitions definition = EnumDefinitions.getEnum(id);
        Map<Long, Object> values = definition.getValues();
        StringBuilder out = new StringBuilder();
        out.append("==== enum ").append(id).append('\n');
        out.append("keyType=").append(definition.keyTypeChar)
                .append(" valueType=").append(definition.valueTypeChar)
                .append(" defaultInt=").append(definition.getDefaultIntValue())
                .append(" defaultString=").append(value(definition.getDefaultStringValue()))
                .append(" entries=").append(values == null ? 0 : values.size()).append('\n');
        appendEntries(out, values);
        return out.toString();
    }

    private static String renderStruct(int id) {
        Map<Long, Object> values = StructDefinitions.getStruct(id).getValues();
        StringBuilder out = new StringBuilder();
        out.append("==== struct ").append(id).append('\n');
        out.append("entries=").append(values == null ? 0 : values.size()).append('\n');
        appendEntries(out, values);
        return out.toString();
    }

    private static String renderParam(Store store, int id) {
        byte[] data = store.getIndex(IndexType.CONFIG).getFile(ArchiveType.PARAMS.getId(), id);
        ParamDefinition definition = decodeParam(data);
        return "==== param " + id + "\n"
                + "type=" + definition.type()
                + " defaultInt=" + definition.defaultInt()
                + " defaultString=" + value(definition.defaultString())
                + " autoDisable=" + definition.autoDisable() + "\n";
    }

    private static ParamDefinition decodeParam(byte[] data) {
        InputStream input = new InputStream(data);
        char type = '\0';
        int defaultInt = 0;
        String defaultString = null;
        boolean autoDisable = true;
        while (true) {
            int opcode = input.readUnsignedByte();
            if (opcode == 0) {
                return new ParamDefinition(type, defaultInt, defaultString, autoDisable);
            }
            switch (opcode) {
                case 1 -> type = cp1252(input.readByte());
                case 2 -> defaultInt = input.readInt();
                case 4 -> autoDisable = false;
                case 5 -> defaultString = input.readString();
                default -> throw new IllegalArgumentException("unknown param opcode " + opcode);
            }
        }
    }

    private static char cp1252(byte value) {
        int unsigned = value & 0xff;
        if (unsigned == 0) {
            throw new IllegalArgumentException("param type has null CP-1252 descriptor");
        }
        return new String(new byte[] {value}, java.nio.charset.Charset.forName("windows-1252"))
                .charAt(0);
    }

    private static void appendEntries(StringBuilder out, Map<Long, Object> values) {
        if (values == null) {
            return;
        }
        values.entrySet().stream()
                .sorted(Map.Entry.comparingByKey(Comparator.naturalOrder()))
                .forEach(entry -> out.append(entry.getKey())
                        .append('\t')
                        .append(value(entry.getValue()))
                        .append('\n'));
    }

    private static String value(Object value) {
        if (!(value instanceof String text)) {
            return String.valueOf(value);
        }
        return '"' + text.replace("\\", "\\\\")
                .replace("\n", "\\n")
                .replace("\r", "\\r")
                .replace("\t", "\\t")
                .replace("\"", "\\\"") + '"';
    }
}
