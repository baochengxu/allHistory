# coding:utf-8
import execjs


def get_ax(key_word):
    t = {"hasGeo": "false", "hasTime": "false", "keyword": "%s" % key_word, "language": "cn"}
    ttt = {
        "data": t,
        "url": "https://www.allhistory.com/api/search/getSuggestion",
    }

    ctx = execjs.compile("""
    one_1  = function(e) {
            var l = "83|83|97|102|101|114|50|52|53|53|76|74|85|89";
            var t = two_1()
              , n = t.n
              , s = t.t
              , u = two_2(e)
              , d = l.split("|").map(function(e) {
                return String.fromCharCode(e)
            }).join("").toString() + n + u;
            c = get_second_string(d)
            return n + ";" + u + ";" + two_1_three_2(10) + ";" + c + ";" + s + ";2;" + two_1().n + ";" + two_1_three_2(80)
        }
        ;
    two_1  = function() {
            var e = arguments.length > 0 && void 0 !== arguments[0] ? arguments[0] : 4
              , t = +new Date
              , n = t
              , i = Number.prototype.toString.call(n, Math.pow(2, e)).split("").reverse().join("");
            return {
                n: two_1_three_1() + i + two_1_three_1(),
                t: t
            }
        }
        ;
    two_2  = function(e) {
            var t = e.data;
            e.url.match(/(https?:)?(\/\/)([^/]*)/) || (e.url = "https://www.allhistory.com" + e.url);
            var n = e.url;
            n += JSON.stringify(t)
            value = get_second_string(n)
            return value
        }
        ;
    two_1_three_1 = function() {
            o = "97_98_99_100_101_102_48_49_50_51_52_53_54_55_56_57"
            for (var e = arguments.length > 0 && void 0 !== arguments[0] ? arguments[0] : 4, t = "", n = o.split("_"), i = 0; i < e; i++) {
                var r = Math.floor(n.length * Math.random());
                t += String.fromCharCode(n[r])
            }
            return t
        }
        ;
    two_1_three_2 = function(number) {
            o = "97_98_99_100_101_102_48_49_50_51_52_53_54_55_56_57"
            for (var e = number, t = "", n = o.split("_"), i = 0; i < e; i++) {
                var r = Math.floor(n.length * Math.random());
                t += String.fromCharCode(n[r])
            }
            return t
        }
        ; 
    
    get_second_string = function(e) {
                        e = three_1(e),
                        e = five_1(e);
                        e = six_1(e.words);
                        zifuchuan  = seven_1(e, 20)
                        return zifuchuan
                    };
    three_1 = function(e) {
                        return {shuzu:four_1(unescape(encodeURIComponent(e))),length:unescape(encodeURIComponent(e)).length}
                    };
    four_1 = function(e) {
                        for (var t = e.length, n = [], i = 0; i < t; i++)
                            n[i >>> 2] |= (255 & e.charCodeAt(i)) << 24 - i % 4 * 8;
                        return n
                    };
    five_1 = function(e) {
                    var t = e.shuzu
                      , n = 8 * e.length
                      , i = 8 * e.length;
                    t[i >>> 5] |= 128 << 24 - i % 32,
                    t[14 + (i + 64 >>> 9 << 4)] = Math.floor(n / 4294967296),
                    t[15 + (i + 64 >>> 9 << 4)] = n;
                    return {words:t,sigBytes:4 * t.length}
                    };
    six_1 = function(e) {
                    words = [1732584193, 4023233417, 2562383102, 271733878, 3285377520]
                    o = []
                    for (var t = 0; t < e.length; t += 16){
                        for (var n = words, i = n[0], r = n[1], a = n[2], s = n[3], l = n[4], u = 0; u < 80; u++) {
                        if (u < 16)
                            o[u] = 0 | e[t + u];
                        else {
                            var d = o[u - 3] ^ o[u - 8] ^ o[u - 14] ^ o[u - 16];
                            o[u] = d << 1 | d >>> 31
                        }
                        var c = (i << 5 | i >>> 27) + l + o[u];
                        c += u < 20 ? 1518500249 + (r & a | ~r & s) : u < 40 ? 1859775393 + (r ^ a ^ s) : u < 60 ? (r & a | r & s | a & s) - 1894007588 : (r ^ a ^ s) - 899497514,
                        l = s,
                        s = a,
                        a = r << 30 | r >>> 2,
                        r = i,
                        i = c
                    }
                    n[0] = n[0] + i | 0,
                    n[1] = n[1] + r | 0,
                    n[2] = n[2] + a | 0,
                    n[3] = n[3] + s | 0,
                    n[4] = n[4] + l | 0
                    }
                return n
                };
    seven_1 = function(words, sigBytes) {
                        for (var t = words, n = sigBytes, i = [], r = 0; r < n; r++) {
                            var o = t[r >>> 2] >>> 24 - r % 4 * 8 & 255;
                            i.push((o >>> 4).toString(16)),
                            i.push((15 & o).toString(16))
                        }
                        return i.join("")
                        };
    """)
    return (ctx.call("one_1", ttt))
