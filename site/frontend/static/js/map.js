
var mapper = {
    map: null,
    hashedMarkers: {},
    turn: true,
    lastZoom: null,
    lastBounds: null,
    infoMarker: null
};
var ajax = {};
var page = {};
var MAP_MARGIN = 40;

page.callback = {};

page.load = function() {
    page.showFilterAsItWas();
    page.overrideFilterSubmit();
    page.enableMapInfoClick();

    if (!GBrowserIsCompatible()) {
        return;
    }
    page.resizeMap();
    var map = new GMap2(document.getElementById("map"));
    map.addControl(new GLargeMapControl());
    map.addControl(new GMapTypeControl());
    map.enableContinuousZoom();
    map.enableScrollWheelZoom();
    new GKeyboardHandler(map);
    if (window.getSight) {
        page._showSight(map, window.getSight());
    } else {
        map.setCenter(new GLatLng(50.087811,14.420460), 12);
    }
    page._showWarm(map);
    mapper.map = map;
    mapper.lastZoom = map.getZoom();

    page.updateClusters();
    GEvent.addListener(map, "moveend", page.updateClusters);
    page.addListener("resize", page.resizeMap);
}

page._showWarm = function(map) {
    var bounds = window.getWarmBounds();
    bounds = new GLatLngBounds(
            new GLatLng(bounds[0][0], bounds[0][1]),
            new GLatLng(bounds[1][0], bounds[1][1]));
    var overlay = new GGroundOverlay("/static/img/warm.png", bounds);
    map.addOverlay(overlay);
}

page._showSight = function(map, sight) {
    var where = new GLatLng(sight.geo[0], sight.geo[1]);
    map.setCenter(where, 14);

    var icon = new GIcon();
    icon.image = "/static/img/circle.png";
    icon.transparent = "/static/img/circle_transparent.png";
    icon.iconSize = new GSize(24, 24);
    icon.iconAnchor = new GPoint(12, 13);
    icon.infoWindowAnchor = new GPoint(11, 13);

    var opts = {
        icon: icon,
        zIndexProcess: page.callback.lowestZIndexProcess
    };
    var marker = new GMarker(where, opts);
    map.addOverlay(marker);
    marker.openInfoWindowHtml(sight.infoHtml);
    marker.bindInfoWindowHtml(sight.infoHtml);
}

page.callback.lowestZIndexProcess = function() {
    return -99999999;
}

page.resizeMap = function() {
    var height = $(window).height() - $("#map").offset().top - MAP_MARGIN;
    if (height < 300) {
        height = 300;
    }
    document.getElementById("map").style.height = height + "px";
    if (mapper.map) {
        mapper.map.checkResize();
        page.updateClusters();
    }
}

page.updateClusters = function() {
    if (mapper.lastZoom != mapper.map.getZoom()) {
        mapper.lastZoom = mapper.map.getZoom();
        mapper.infoMarker = null;
        // let the tiles to load first
        window.setTimeout(page.updateClusters, 100);
        return;
    }
    mapper._getClusters();
}

mapper._getClusters = function(afterUpdateCallback) {
    var me = this;
    var bounds = me.map.getBounds();
    me.lastBounds = bounds;
    ajax.sendGet("/ajax/cluster", {
            "sw": bounds.getSouthWest().toUrlValue(),
            "ne": bounds.getNorthEast().toUrlValue(),
            "zoom": me.map.getZoom()
            },
    function (data) {
        if (me.lastBounds !== bounds) {
            console.info("response for old bounds:", bounds);
        } else {
            page.id("mapInfo").innerHTML = data.info;
            var markers = data.markers;
            for (var i = 0, cluster; cluster = markers[i]; i++) {
                me._addMarker(cluster);
            }
            me._stabilizeInfoMarker();
            me._clearOldMarkers();
        }
        if (afterUpdateCallback) {
            afterUpdateCallback();
        }
    });
}

mapper._addMarker = function(cluster) {
    var key = [cluster.geo, cluster.size];
    var existing = this.hashedMarkers[key];
    if (existing) {
        existing.turn = this.turn;
        return;
    }

    var where = new GLatLng(cluster.geo[0], cluster.geo[1]);
    var icon = this._getIcon(cluster.color,
            24 + Math.floor(4*Math.log(cluster.size)));
    var opts = {
        title: cluster.size,
        icon: icon
    };
    var marker = new GMarker(where, opts);
    this.map.addOverlay(marker);
    marker.turn = this.turn;
    this.hashedMarkers[key] = marker;
    marker.bindInfoWindowHtml(cluster.newestHtml);
    GEvent.addListener(marker, "mouseover", page.callback.onMouseOverMarker);
    GEvent.addListener(marker, "mouseout", page.callback.onMouseOutMarker);
    GEvent.addListener(marker, "infowindowopen",
            page.callback.onInfoWindowOpenMarker);
}

mapper._clearOldMarkers = function() {
    var counter = 0;
    var deleted = 0;
    for (var key in this.hashedMarkers) {
        var marker = this.hashedMarkers[key];
        if (marker.turn != this.turn) {
            this.map.removeOverlay(marker);
            delete this.hashedMarkers[key];
            deleted += 1;
        }
        counter += 1;
    }
    console.debug("deleted:", deleted, counter);
    this.turn = !this.turn;
}

mapper._getIcon = function(color, size) {
    size += size % 2;
    var opts = {
        width: size,
        height: size,
        primaryColor: color,
        cornerColor: "FFFFFF",
        strokeColor: "000000"
    };
    icon = MapIconMaker.createMarkerIcon(opts);
    delete icon.printImage;
    delete icon.mozPrintImage;
    return icon;
}

mapper._stabilizeInfoMarker = function() {
    if (this.infoMarker) {
        this.infoMarker.turn = this.turn;
    }
}

/**
 * Zooms to a marker from an InfoWindow link.
 */
mapper.zoomIn = function() {
    var point = this.map.getInfoWindow().getPoint();
    var maxZoom = this.map.getCurrentMapType().getMaximumResolution();
    if (this.map.getZoom() < maxZoom) {
        this.map.setCenter(point, this.map.getZoom() + 1);
    } else {
        this.map.panTo(point);
    }
    return false;
}

ajax.sendGet = function(url, params, callback) {
    url = url + this._encodeParams(params);
    GDownloadUrl(url, function (data, responseCode) {
        if (responseCode != 200) {
            console.error("Ajax error", url, responseCode);
            return;
        }
        data = eval("(" + data + ")");
        callback(data);
    });
}

ajax._encodeParams = function(params) {
    var urlParams = [];
    for (var key in params) {
        var value = params[key];

        if (value == undefined) {
            continue;
        }
        if (urlParams.length == 0) {
            urlParams.push("?");
        } else {
            urlParams.push("&");
        }

        urlParams.push(encodeURIComponent(key));
        urlParams.push("=");
        urlParams.push(encodeURIComponent(value));
    }
    return urlParams.join('');
}

page.callback.onMouseOverMarker = function() {
    var marker = this;
    var url = marker.getIcon().image;
    url = url.replace(/chco=([0-9a-fA-F]+),([0-9a-fA-F]+),([0-9a-fA-F]+)/, "chco=$1,$2,FFFFFF");
    marker.setImage(url);
}

page.callback.onMouseOutMarker = function() {
    var marker = this;
    marker.setImage(marker.getIcon().image);
}

page.callback.onInfoWindowOpenMarker = function() {
    mapper.infoMarker = this;
}

page.enableMapInfoClick = function() {
    $("#mapInfo").click(function(event) {
        var target = $(event.target);
        if (!target.is("a")) {
            return true;
        }

        event.preventDefault();
        event.stopPropagation();
        page.toggleFilter();
    });
}

page.showFilterAsItWas = function() {
    if (page.readCookie("sf")) {
        page.showFilter();
    }
}

page.overrideFilterSubmit = function() {
    $("#filter").submit(function(event) {
        event.preventDefault();
        event.stopPropagation();

        var form = $(this);
        var params = {};
        $(":input", this).each(function() {
            params[this.name] = this.value;
        });
        ajax.sendGet("/ajax/filter", params, function(data) {
            mapper.infoMarker = null;
            mapper._getClusters(function() {
                form.removeClass("sent");
                $(":submit", form).get(0).disabled = false;
            });
        });
        form.addClass("sent");
        $(":submit", form).get(0).disabled = true;
    });
}

page.toggleFilter = function() {
    if (page.readCookie("sf")) {
        page.hideFilter();
    } else {
        page.showFilter();
    }
}

page.showFilter = function() {
    // konqueror does not supports display = ""
    page.id("showFilter").style.display = "none";
    page.id("hideFilter").style.display = "block";
    page.id("filter").style.display = "block";
    page.createCookie("sf", "1", 20);
}

page.hideFilter = function() {
    page.id("showFilter").style.display = "block";
    page.id("hideFilter").style.display = "none";
    page.id("filter").style.display = "none";
    page.createCookie("sf", "", -1);
}

page.id = function(id) {
    return document.getElementById(id);
}

// Cookies
page.createCookie = function(name, value, years) {
    var date = new Date();
    date.setTime(date.getTime() + years*356*24*3600*1000);
    var expires = "; expires=" + date.toUTCString();
    document.cookie = [name, "=", window.encodeURIComponent(value), expires, "; path=/"].join('');
}

page.readCookie = function(name) {
    if (!document.cookie || document.cookie == "") {
        return undefined;
    }

    var nameEQ = name + "=";
    var cookies = document.cookie.split(';');
    for (var i = 0, item; item = cookies[i]; i++) {
        item = item.replace(/^ +/, "");
        if (item.indexOf(nameEQ) == 0) {
            return window.decodeURIComponent(item.substring(nameEQ.length, item.length));
        }
    }
    return undefined;
}

// Events
page.addListener = function (name, callback) {
    if (window.attachEvent) {
        window.attachEvent("on" + name, callback);
    } else {
        window.addEventListener(name, callback, false);
    }
}

page.addListener("load", page.load);
// don't use unload when it is not needed to allow bfcache
if (window.attachEvent) {
    page.addListener("unload", GUnload);
} else {
    $(window).unbind("unload");
}

if (!window.console) {
    var names = ["log", "debug", "info", "warn", "error", "assert", "dir", "dirxml",
    "group", "groupEnd", "time", "timeEnd", "count", "trace", "profile", "profileEnd"];

    window.console = {};
    for (var i = 0; i < names.length; ++i) {
        window.console[names[i]] = function() {};
    }
}

