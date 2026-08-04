import com.rs.cache.Cache;
import com.rs.cache.Index;
import com.rs.cache.IndexType;
import com.rs.cache.Store;
import com.rs.cache.loaders.interfaces.IComponentDefinitions;

import java.io.File;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.List;
import java.util.Locale;

/** Read-only query tool for client interface definitions in a disk cache. */
final class OpenRs2InterfaceQuery {
    private OpenRs2InterfaceQuery() {}

    public static void main(String[] args) throws Exception {
        if (args.length < 2) {
            usage();
            System.exit(2);
        }

        String cacheDirectory = args[0].endsWith(File.separator)
                ? args[0]
                : args[0] + File.separator;
        Store store = new Store(cacheDirectory, false);
        Cache.STORE = store;
        String mode = args[1].toLowerCase(Locale.ROOT);

        switch (mode) {
            case "count" -> printCount(store);
            case "dump" -> {
                if (args.length < 3) {
                    usage();
                    System.exit(2);
                }
                int interfaceId = Integer.parseInt(args[2]);
                int[] componentIds = Arrays.stream(args, 3, args.length)
                        .mapToInt(Integer::parseInt)
                        .toArray();
                System.out.print(renderInterface(store, interfaceId, componentIds));
            }
            case "find" -> {
                if (args.length != 3) {
                    usage();
                    System.exit(2);
                }
                printMatches(store, args[2]);
            }
            default -> {
                usage();
                System.exit(2);
            }
        }
    }

    private static void usage() {
        System.err.println(
                "usage: OpenRs2InterfaceQuery <cache-dir> "
                        + "<count|dump|find> [interface-id [component-id ...]|needle]"
        );
    }

    private static List<Integer> existingInterfaces(Store store) {
        Index index = store.getIndex(IndexType.INTERFACES);
        List<Integer> ids = new ArrayList<>();
        for (int id = 0; id <= index.getLastArchiveId(); id++) {
            if (index.archiveExists(id)) {
                ids.add(id);
            }
        }
        return ids;
    }

    private static void printCount(Store store) {
        Index index = store.getIndex(IndexType.INTERFACES);
        List<Integer> ids = existingInterfaces(store);
        long components = ids.stream()
                .mapToLong(index::getValidFilesCount)
                .sum();
        int first = ids.isEmpty() ? -1 : ids.getFirst();
        int last = ids.isEmpty() ? -1 : ids.getLast();
        System.out.printf(
                "index=%d interfaces=%d components=%d firstId=%d lastId=%d%n",
                index.getId(), ids.size(), components, first, last
        );
    }

    private static String renderInterface(Store store, int interfaceId, int[] componentIds) {
        if (!store.getIndex(IndexType.INTERFACES).archiveExists(interfaceId)) {
            return "==== interface " + interfaceId + " absent\n";
        }
        IComponentDefinitions[] components = IComponentDefinitions.getInterface(interfaceId);
        StringBuilder out = new StringBuilder();
        out.append("==== interface ").append(interfaceId)
                .append(" components=").append(components.length).append('\n');
        if (componentIds.length == 0) {
            for (IComponentDefinitions component : components) {
                appendComponent(out, component);
            }
        } else {
            for (int componentId : componentIds) {
                if (componentId < 0 || componentId >= components.length
                        || components[componentId] == null) {
                    out.append("-- component ").append(componentId).append(" absent\n");
                } else {
                    appendComponent(out, components[componentId]);
                }
            }
        }
        return out.toString();
    }

    private static void printMatches(Store store, String rawNeedle) {
        String needle = rawNeedle.toLowerCase(Locale.ROOT);
        for (int interfaceId : existingInterfaces(store)) {
            IComponentDefinitions[] components;
            try {
                components = IComponentDefinitions.getInterface(interfaceId);
            } catch (IllegalStateException error) {
                if (!"if1".equals(error.getMessage())) {
                    throw error;
                }
                System.err.println(
                        "skipped unsupported IF1 interface " + interfaceId
                );
                continue;
            }
            for (IComponentDefinitions component : components) {
                if (component != null && searchableText(component).toLowerCase(Locale.ROOT)
                        .contains(needle)) {
                    StringBuilder out = new StringBuilder();
                    appendComponent(out, component);
                    System.out.print(out);
                }
            }
        }
    }

    private static String searchableText(IComponentDefinitions component) {
        return String.join("\n",
                value(component.name),
                value(component.text),
                value(component.useOnName),
                value(component.opName),
                value(component.useOptionString),
                component.optionNames == null ? "" : String.join("\n", component.optionNames)
        );
    }

    private static void appendComponent(
            StringBuilder out,
            IComponentDefinitions component
    ) {
        if (component == null) {
            return;
        }
        out.append("-- component ").append(component.interfaceId).append(':')
                .append(component.componentId)
                .append(" uid=").append(component.uid)
                .append(" type=").append(component.type)
                .append(" name=").append(value(component.name))
                .append(" parent=").append(component.parent)
                .append(" hidden=").append(component.hidden)
                .append(" contentType=").append(component.contentType)
                .append('\n');
        out.append("bounds=").append(component.basePositionX).append(',')
                .append(component.basePositionY).append(',')
                .append(component.baseWidth).append(',')
                .append(component.baseHeight)
                .append(" aspect=").append(component.aspectXType).append(',')
                .append(component.aspectYType).append(',')
                .append(component.aspectWidthType).append(',')
                .append(component.aspectHeightType)
                .append(" noClickThrough=").append(component.noClickThrough)
                .append('\n');
        out.append("text=").append(value(component.text))
                .append(" fontId=").append(component.fontId)
                .append(" spriteId=").append(component.spriteId)
                .append(" modelType=").append(component.modelType)
                .append(" modelId=").append(component.modelId)
                .append('\n');
        out.append("useOnName=").append(value(component.useOnName))
                .append(" opName=").append(value(component.opName))
                .append(" useOptionString=").append(value(component.useOptionString))
                .append(" options=").append(stringArray(component.optionNames))
                .append('\n');
        out.append("usesScripts=").append(component.usesScripts)
                .append(" onLoad=").append(objectArray(component.onLoadScript))
                .append(" onHover=").append(objectArray(component.onMouseHoverScript))
                .append(" onLeave=").append(objectArray(component.onMouseLeaveScript))
                .append(" onUse=").append(objectArray(component.anObjectArray1400))
                .append(" popup=").append(objectArray(component.popupScript))
                .append('\n');
    }

    private static String objectArray(Object[] values) {
        if (values == null) {
            return "null";
        }
        return Arrays.toString(values);
    }

    private static String stringArray(String[] values) {
        if (values == null) {
            return "null";
        }
        return Arrays.stream(values)
                .map(OpenRs2InterfaceQuery::value)
                .toList()
                .toString();
    }

    private static String value(String value) {
        if (value == null) {
            return "null";
        }
        return '"' + value.replace("\\", "\\\\")
                .replace("\n", "\\n")
                .replace("\r", "\\r")
                .replace("\t", "\\t")
                .replace("\"", "\\\"") + '"';
    }
}
