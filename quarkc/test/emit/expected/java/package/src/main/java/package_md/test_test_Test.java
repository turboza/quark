package package_md;

public class test_test_Test extends quark.reflect.Class implements io.datawire.quark.runtime.QObject {
    public static quark.reflect.Class singleton = new test_test_Test();
    public test_test_Test() {
        super("test.test.Test");
        (this).name = "test.test.Test";
        (this).parameters = new java.util.ArrayList(java.util.Arrays.asList(new Object[]{}));
        (this).fields = new java.util.ArrayList(java.util.Arrays.asList(new Object[]{new quark.reflect.Field("quark.int", "size")}));
        (this).methods = new java.util.ArrayList(java.util.Arrays.asList(new Object[]{new test_test_Test_go_Method()}));
    }
    public Object construct(java.util.ArrayList<Object> args) {
        return new test.test.Test();
    }
    public String _getClass() {
        return (String) (null);
    }
    public Object _getField(String name) {
        return null;
    }
    public void _setField(String name, Object value) {}
}
