import QtQuick 2.15
import QtQuick.Controls 2.15

ListView {
    id: wheel
    property int itemHeight: 40
    property alias currentIndex: wheel.currentIndex
    property var model: []

    width: 80
    height: 120
    model: model
    clip: true
    snapMode: ListView.SnapToItem
    boundsBehavior: Flickable.StopAtBounds
    preferredHighlightBegin: (height - itemHeight) / 2
    preferredHighlightEnd: (height + itemHeight) / 2
    highlightRangeMode: ListView.StrictlyEnforceRange
    highlightMoveDuration: 150

    delegate: Item {
        width: wheel.width
        height: wheel.itemHeight

        Text {
            anchors.centerIn: parent
            text: modelData < 10 ? "0" + modelData : modelData
            font.pixelSize: 32
            color: "#d1d1d6"
        }
    }
}