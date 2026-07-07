import com.rs.cache.Cache;
import com.rs.cache.loaders.EnumDefinitions;
import com.rs.cache.loaders.ItemDefinitions;

import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.ArrayList;
import java.util.LinkedHashSet;
import java.util.List;
import java.util.Set;

public final class DumpDarkanShopPriceInputs {
    private DumpDarkanShopPriceInputs() {
    }

    public static void main(String[] args) throws Exception {
        if (args.length != 3) {
            throw new IllegalArgumentException("usage: DumpDarkanShopPriceInputs <cache-path> <item-id-file> <output-json>");
        }

        Cache.init(args[0]);
        Set<Integer> itemIds = readItemIds(Path.of(args[1]));
        EnumDefinitions coinBuy = EnumDefinitions.getEnum(733);
        EnumDefinitions coinSell = EnumDefinitions.getEnum(1441);
        EnumDefinitions tokkulBuy = EnumDefinitions.getEnum(731);
        EnumDefinitions tokkulSell = EnumDefinitions.getEnum(732);

        StringBuilder json = new StringBuilder();
        json.append("{\n  \"items\": {\n");
        boolean first = true;
        for (int itemId : itemIds) {
            if (!first) {
                json.append(",\n");
            }
            first = false;
            json.append("    \"").append(itemId).append("\": ");
            try {
                ItemDefinitions defs = ItemDefinitions.getDefs(itemId);
                if (defs == null) {
                    json.append("{\"error\":\"missing_definition\"}");
                    continue;
                }
                json.append("{")
                        .append("\"value\":").append(defs.getValue()).append(',')
                        .append("\"stackable\":").append(defs.stackable).append(',')
                        .append("\"sell_price\":").append(defs.getSellPrice()).append(',')
                        .append("\"coin_buy_override\":").append(coinBuy.getIntValue(itemId)).append(',')
                        .append("\"coin_sell_override\":").append(coinSell.getIntValue(itemId)).append(',')
                        .append("\"tokkul_buy_override\":").append(tokkulBuy.getIntValue(itemId)).append(',')
                        .append("\"tokkul_sell_override\":").append(tokkulSell.getIntValue(itemId))
                        .append("}");
            } catch (Throwable error) {
                json.append("{\"error\":\"").append(jsonEscape(error.getClass().getSimpleName())).append("\"}");
            }
        }
        json.append("\n  }\n}\n");
        Files.writeString(Path.of(args[2]), json.toString(), StandardCharsets.UTF_8);
    }

    private static Set<Integer> readItemIds(Path path) throws Exception {
        List<String> lines = Files.readAllLines(path, StandardCharsets.UTF_8);
        List<Integer> ids = new ArrayList<>();
        for (String line : lines) {
            String clean = line.trim();
            if (clean.isEmpty()) {
                continue;
            }
            ids.add(Integer.parseInt(clean));
        }
        return new LinkedHashSet<>(ids);
    }

    private static String jsonEscape(String value) {
        return value.replace("\\", "\\\\").replace("\"", "\\\"");
    }
}
