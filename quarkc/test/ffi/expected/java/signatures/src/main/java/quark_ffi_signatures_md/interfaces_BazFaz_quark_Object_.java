package quark_ffi_signatures_md;

public class interfaces_BazFaz_quark_Object_ extends quark.reflect.Class implements io.datawire.quark.runtime.QObject {
    public static quark.reflect.Class singleton = new interfaces_BazFaz_quark_Object_();
    public interfaces_BazFaz_quark_Object_() {
        super("interfaces.BazFaz<quark.Object>");
        (this).name = "interfaces.BazFaz";
        (this).parameters = new java.util.ArrayList(java.util.Arrays.asList(new Object[]{"quark.Object"}));
        (this).fields = new java.util.ArrayList(java.util.Arrays.asList(new Object[]{}));
        (this).methods = new java.util.ArrayList(java.util.Arrays.asList(new Object[]{new interfaces_BazFaz_quark_Object__m1_Method(), new interfaces_BazFaz_quark_Object__m2_Method(), new interfaces_BazFaz_quark_Object__m3_Method()}));
        (this).parents = new java.util.ArrayList(java.util.Arrays.asList(new Object[]{"quark.Object"}));
    }
    public Object construct(java.util.ArrayList<Object> args) {
        return new interfaces.BazFaz<Object>();
    }
    public Boolean isAbstract() {
        return false;
    }
    public String _getClass() {
        return (String) (null);
    }
    public Object _getField(String name) {
        return null;
    }
    public void _setField(String name, Object value) {}
}
