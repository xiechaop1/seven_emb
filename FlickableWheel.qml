import QtQuick 2.15
import QtQuick.Controls 2.15

ListView {
    id: wheel

    // ✅ 自定义属性
    property int itemHeight: 40
    property int currentIndex: wheel.currentIndex

    width: 80
    height: 120
    clip: true
    model: 10  // 默认模型，外部可以覆盖

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