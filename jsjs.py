function(e)
{
    var
t = e.data;
e.url.match( / (https?:)?(\ / \ /)([ ^ /] * ) / ) | | (e.url = window.location.origin + e.url);
var
n = e.url;
t & & (0,
       i.default)(t).length & & (n += (0,
o.default)(t));
return (0,
        r.default)(n).toString()
}
;