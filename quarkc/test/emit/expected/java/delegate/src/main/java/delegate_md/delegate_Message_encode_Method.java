package delegate_md;

public class delegate_Message_encode_Method extends quark.reflect.Method implements io.datawire.quark.runtime.QObject {
    public delegate_Message_encode_Method() {
        super("quark.String", "encode", new java.util.ArrayList(java.util.Arrays.asList(new Object[]{})));
    }
    public Object invoke(Object object, java.util.ArrayList<Object> args) {
        delegate.Message obj = (delegate.Message) (object);
        return (obj).encode();
    }
    public String _getClass() {
        return (String) (null);
    }
    public Object _getField(String name) {
        return null;
    }
    public void _setField(String name, Object value) {}
}
