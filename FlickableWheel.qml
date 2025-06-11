import QtQuick 2.15
import QtQuick.Controls 2.15

Item {
    id: root
    width: 80
    height: 120

    property int itemHeight: 40
    property int currentIndex: listView.currentIndex
    property alias model: listView.model

    ListView {
        id: listView
        anchors.fill: parent
        clip: true

        snapMode: ListView.SnapToItem
        boundsBehavior: Flickable.StopAtBounds
        preferredHighlightBegin: (height - itemHeight) / 2
        preferredHighlightEnd: (height + itemHeight) / 2
        highlightRangeMode: ListView.StrictlyEnforceRange
        highlightMoveDuration: 150

        delegate: Item {
            width: root.width
            height: root.itemHeight
            Rectangle {
                anchors.fill: parent
                color: index === root.currentIndex ? "#232325ee" : "transparent"
                radius: 8
            }
            Text {
                anchors.centerIn: parent
                text: modelData < 10 ? "0" + modelData : modelData
                font.pixelSize: 32
                font.weight: Font.DemiBold
                color: index === root.currentIndex ? "white" : "#8e8e93"
                horizontalAlignment: Text.AlignHCenter
                verticalAlignment: Text.AlignVCenter
            }
        }
    }
}