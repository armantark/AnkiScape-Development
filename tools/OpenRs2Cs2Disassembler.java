import com.rs.cache.Cache;
import com.rs.cache.Index;
import com.rs.cache.IndexType;
import com.rs.cache.Store;
import com.rs.cache.loaders.cs2.CS2Instruction;
import com.rs.cache.loaders.cs2.CS2Script;
import com.rs.lib.io.InputStream;

import java.io.File;
import java.util.ArrayList;
import java.util.List;

/**
 * Linear disassembler for client scripts (CS2) held in js5 cache index 12.
 *
 * Index 12 is established from the deobfuscated client's loader table
 * (darkan-client IndexLoaders: CS2_SCRIPTS_INDEX = INDEX_12) and agrees with
 * Darkan core's IndexType.CS2_SCRIPTS. Each script is archive=scriptId, file 0.
 *
 * IMPORTANT REVISION LIMIT: Jagex renumbered the CS2 opcode table after build
 * 727. Darkan core carries only the 727 table, so this tool decodes the
 * 727-2012-07-24 cache and fails on 652/728/729/736/741/742 with
 * "Invalid operation code" or a short operations array. Script *bytes* in the
 * other builds can still be compared structurally (length, constant offsets).
 *
 * Build the classpath the same way tools/query_openrs2_cache.sh does:
 *   CP=$(find ~/.gradle/caches/modules-2/files-2.1 -name '*.jar' | paste -sd: -)
 *   /opt/homebrew/opt/openjdk@25/bin/java --class-path "$CP" \
 *       tools/OpenRs2Cs2Disassembler.java <cache-dir> <mode> [args]
 *
 * Modes:
 *   count                                 index id and archive counts
 *   dump    <scriptId> [scriptId ...]      linear opcode listing
 *   scan    <opNameSubstr|*> [operand|lo-hi ...]
 *                                         find scripts by opcode name and/or
 *                                         int operand (component ids, varp ids)
 *   grepstr <needle>                       find scripts pushing a string
 *
 * Jump semantics for reading the listings: conditional opcodes (INT_EQ, INT_LT,
 * ...) and GOTO carry a relative operand; the target index is pc + 1 + operand.
 */
final class OpenRs2Cs2Disassembler {

    private OpenRs2Cs2Disassembler() {}

    public static void main(String[] args) throws Exception {
        if (args.length < 2) {
            System.err.println("usage: OpenRs2Cs2Disassembler <cache-dir> <count|dump|scan|grepstr> [args]");
            System.exit(2);
        }

        String cacheDirectory = args[0].endsWith(File.separator) ? args[0] : args[0] + File.separator;
        Store store = new Store(cacheDirectory, false);
        Cache.STORE = store;
        Index scripts = store.getIndex(IndexType.CS2_SCRIPTS);
        String mode = args[1];

        switch (mode) {
            case "count" -> System.out.printf("index=%d lastArchive=%d validArchives=%d%n",
                    scripts.getId(), scripts.getLastArchiveId(), scripts.getValidArchivesCount());
            case "dump" -> {
                for (int i = 2; i < args.length; i++) {
                    int id = Integer.parseInt(args[i]);
                    CS2Script script = load(scripts, id);
                    if (script == null) {
                        System.out.println("script " + id + ": absent or undecodable");
                    } else {
                        print(id, script);
                    }
                }
            }
            case "scan" -> scan(scripts, args);
            case "grepstr" -> grepstr(scripts, args[2].toLowerCase());
            default -> throw new IllegalArgumentException("unknown mode " + mode);
        }
    }

    private static void scan(Index scripts, String[] args) {
        String nameFilter = args[2];
        List<Integer> wanted = new ArrayList<>();
        for (int i = 3; i < args.length; i++) {
            String value = args[i];
            int dash = value.indexOf('-', 1);
            if (dash > 0) {
                int low = Integer.parseInt(value.substring(0, dash));
                int high = Integer.parseInt(value.substring(dash + 1));
                for (int v = low; v <= high; v++) {
                    wanted.add(v);
                }
            } else {
                wanted.add(Integer.parseInt(value));
            }
        }
        for (int id = 0; id <= scripts.getLastArchiveId(); id++) {
            CS2Script script = load(scripts, id);
            if (script == null || script.operations == null) {
                continue;
            }
            for (int op = 0; op < script.operations.length; op++) {
                CS2Instruction instruction = script.operations[op];
                if (instruction == null) {
                    continue;
                }
                String name = instruction.name();
                if (!nameFilter.equals("*") && !name.contains(nameFilter)) {
                    continue;
                }
                int operand = script.intOpValues == null ? -1 : script.intOpValues[op];
                if (wanted.isEmpty() || wanted.contains(operand)) {
                    System.out.printf("script %d op %d %s %d%n", id, op, name, operand);
                }
            }
        }
    }

    private static void grepstr(Index scripts, String needle) {
        for (int id = 0; id <= scripts.getLastArchiveId(); id++) {
            CS2Script script = load(scripts, id);
            if (script == null || script.stringOpValues == null) {
                continue;
            }
            for (int op = 0; op < script.stringOpValues.length; op++) {
                String value = script.stringOpValues[op];
                if (value != null && value.toLowerCase().contains(needle)) {
                    System.out.printf("script %d op %d \"%s\"%n", id, op, value);
                }
            }
        }
    }

    private static CS2Script load(Index scripts, int id) {
        byte[] data;
        try {
            data = scripts.getFile(id, 0);
        } catch (RuntimeException ignored) {
            return null;
        }
        if (data == null || data.length <= 1) {
            return null;
        }
        try {
            return new CS2Script(new InputStream(data));
        } catch (RuntimeException | Error e) {
            if (System.getenv("CS2_VERBOSE") != null) {
                System.out.println("script " + id + " decode failed: " + e);
            }
            return null;
        }
    }

    private static void print(int id, CS2Script script) {
        System.out.printf("==== script %d name=%s intArgs=%d strArgs=%d longArgs=%d "
                        + "intLocals=%d strLocals=%d longLocals=%d ops=%d%n",
                id, script.name, script.intArgsCount, script.stringArgsCount, script.longArgsCount,
                script.intLocalsCount, script.stringLocalsCount, script.longLocalsCount,
                script.operations == null ? 0 : script.operations.length);
        if (script.switchMaps != null) {
            for (int i = 0; i < script.switchMaps.length; i++) {
                System.out.printf("  switchMap[%d] = %s%n", i, script.switchMaps[i]);
            }
        }
        for (int i = 0; i < script.operations.length; i++) {
            CS2Instruction instruction = script.operations[i];
            String name = instruction == null ? "OPCODE_" + script.operationOpcodes[i] : instruction.name();
            String operand;
            if (instruction == CS2Instruction.PUSH_STRING) {
                operand = "\"" + (script.stringOpValues == null ? null : script.stringOpValues[i]) + "\"";
            } else if (instruction == CS2Instruction.PUSH_LONG) {
                operand = String.valueOf(script.longOpValues == null ? 0 : script.longOpValues[i]);
            } else {
                operand = String.valueOf(script.intOpValues == null ? 0 : script.intOpValues[i]);
            }
            System.out.printf("  %4d  %-28s %s%n", i, name, operand);
        }
    }
}
