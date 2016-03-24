package pkg;

public class StringBox extends Box<String> implements io.datawire.quark.runtime.QObject {
    public static quark.reflect.Class pkg_Box_quark_String__ref = parameterized_defaults_md.Root.pkg_Box_quark_String__md;
    public static quark.reflect.Class pkg_StringBox_ref = parameterized_defaults_md.Root.pkg_StringBox_md;
    public StringBox(String contents) {
        super(contents);
    }
    public String _getClass() {
        return "pkg.StringBox";
    }
    public Object _getField(String name) {
        if ((name)==("contents") || ((Object)(name) != null && ((Object) (name)).equals("contents"))) {
            return (this).contents;
        }
        return null;
    }
    public void _setField(String name, Object value) {
        if ((name)==("contents") || ((Object)(name) != null && ((Object) (name)).equals("contents"))) {
            (this).contents = (String) (value);
        }
    }
}
