// vim: fdm=indent

function sleep(timeoutInMs) {
    // Asynchronous sleep.
    return new Promise(resolve => setTimeout(resolve, timeoutInMs));
}

function findReact(dom) {
    // Get the React object corresponding to a DOM element.
    // https://stackoverflow.com/a/39165137
    let key = Object.keys(dom).find(key=>key.startsWith("__reactInternalInstance$"));
    let internalInstance = dom[key];
    if (internalInstance == null) return null;
    if (internalInstance.return) { // react 16+
        return internalInstance._debugOwner
            ? internalInstance._debugOwner.stateNode
            : internalInstance.return.stateNode;
    }
    else { // react <16
        return internalInstance._currentElement._owner._instance;
    }
}

function CardToBoulder(card) {
    // Get the React boulder object from the DOM card it was rendered into.
    let reactInstance = findReact(card);
    let boulder = reactInstance.props.children[0].props.children.props.boulder;
    return boulder;
}

function getBoulders() {
    // Get all boulders rendered on the page.
    let cards = document.querySelectorAll("div[class^=card-card");
    return Array.prototype.map.call(cards, CardToBoulder);
}

async function getTotalBouldersCount() {
    // Count the total number of boulders in the gym.
    let bouldersCount = null;
    while (bouldersCount == null) {
        span = $("#react-root span")[0];
        if (span != null) {
            bouldersCount = findReact(span).props.bouldersCount;
        }
        await sleep(500);
    }
    return bouldersCount;
}

function getRenderedBouldersCount() {
    // Count the number of rendered boulder elements on the page.
    return getBoulders().length;
}

function boulderToList(b) {
    // Convert a boulder object into a list.
    let output = [];

    output.push(["Title", String(b.getTitle())]);
    output.push(["Description", String(b.getDescription())]);
    output.push(["HoldsColor", String(b.getHoldsColor())]);
    output.push(["GradeText", String(b.getGradeText())]);
    output.push(["Label", String(b.getLabel())]);
    output.push(["RouteTypes", String(b.getRouteTypes())]);
    output.push(["Points", b.getPoints()]);
    output.push(["UserPoints", b.getUserPoints()]);
    output.push(["Zone", b.getZone()]);
    output.push(["Date", String(b.getDate())]);
    output.push(["Closed", String(b.getClosed())]);
    output.push(["Url", String(b.getUrl())]);
    output.push(["PictureUrl", String(b.getPictureUrl())]);
    output.push(["PictureZoom", String(b.getPictureZoom())]);
    output.push(["HoldsColorHexa", String(b.getHoldsColorHexa())]);
    output.push(["HalfLabelHexa", String(b.getHalfLabelHexa())]);
    output.push(["Modified", String(b.getModified())]);
    output.push(["ModifiedValues", String(b.getModifiedValues())]);
    output.push(["Modifier", String(b.getModifier())]);
    output.push(["PictureSrc", String(b.getPictureSrc())]);
    // output.push(["PictureSrcSet", String(b.getPictureSrcSet())]);

    return output;
}

async function scrollToBottom() {
    // Scroll down until all boulders are rendered
    window.log_comm.receive('scrolling');
    let totalBouldersCount = await getTotalBouldersCount();
    window.log_comm.receive('total boulders count: ' + totalBouldersCount);
    while (totalBouldersCount > getRenderedBouldersCount()) {
        window.log_comm.receive(
            'rendered / scroll height: '
            + getRenderedBouldersCount()
            + ' / '
            + document.body.scrollHeight
            );
        window.scrollTo(0, document.body.scrollHeight);
        await sleep(1000);
    }
}

$.getScript("qrc:///qtwebchannel/qwebchannel.js", function() {
    new QWebChannel(qt.webChannelTransport, function (channel) {
        window.log_comm = channel.objects.log_comm;
        window.data_comm = channel.objects.data_comm;
        log_comm.receive('Initiated communication');
        scrollToBottom().then(function() {
            let boulders = getBoulders();
            log_comm.receive('parsed boulders: ' + boulders.length);
            for (let b of boulders) {
                data_comm.receive(boulderToList(b));
            }
            log_comm.quitApp();
        });
    });
});
