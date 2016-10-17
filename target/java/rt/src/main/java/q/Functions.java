package q;

import java.util.Map;
import java.util.HashMap;

public class Functions {
    public static boolean object__ne__(Object left, Object right) { return left == right; }

    public static void print(String msg) { System.out.println(msg); }

    public static boolean int__eq__ (int i, int j) { return i == j; }
    public static int     int__add__(int i, int j) { return i + j; }
    public static int     int__sub__(int i, int j) { return i - j; }

    private static String null_check(String value) {
        if (value != null) {
            return value;
        } else {
            return "";
        }
    }
    private static int null_check(Integer value) {
        if (value != null) {
            return value;
        } else {
            return 0;
        }
    }

    public static Map<String,String> map_string_string__init__() {
        return new HashMap<String,String>();
    }
    public static String map_string_string__get__(Map<String,String> map, String key) {
        String ret = map.get(key);
        return null_check(ret);
    }
    public static void map_string_string__set__(Map<String,String> map, String key, String value) {
        map.put(key, value);
    }
    public static int map_string_string__len__(Map<String,String> map) {
        return map.size();
    }


    public static Map<String,Integer> map_string_int__init__() {
        return new HashMap<String,Integer>();
    }
    public static int map_string_int__get__(Map<String,Integer> map, String key) {
        Integer ret = map.get(key);
        return null_check(ret);
    }
    public static void map_string_int__set__(Map<String,Integer> map, String key, int value) {
        map.put(key, value);
    }
    public static int map_string_int__len__(Map<String,Integer> map) {
        return map.size();
    }
}
