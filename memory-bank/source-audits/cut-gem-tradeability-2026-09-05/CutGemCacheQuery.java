import com.rs.cache.loaders.ItemDefinitions;

final class CutGemCacheQuery {
    private static void describe(Class<?> type) {
        System.out.printf(
                "CLASS %s source=%s implementation_version=%s specification_version=%s%n",
                type.getName(),
                type.getProtectionDomain().getCodeSource().getLocation().toExternalForm(),
                type.getPackage().getImplementationVersion(),
                type.getPackage().getSpecificationVersion());
    }

    public static void main(String[] args) throws Exception {
        System.out.println("INPUT_CACHE " + args[0]);
        describe(ItemDefinitions.class);
        describe(OpenRs2CacheItemSearch.class);
        OpenRs2CacheItemSearch.main(args);
    }
}
