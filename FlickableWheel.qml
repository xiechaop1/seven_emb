import QtQuick 2.15
import QtQuick.Controls 2.15

ListView {
    id: wheel
    property alias currentIndex: wheel.currentIndex
    property alias modelData: wheel.model   // 👈 注意这里是 alias，不是新定义

    width: 80
    height: 120
    itemHeight: 40
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