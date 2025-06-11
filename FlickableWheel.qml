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

            Text {
                anchors.centerIn: parent
                text: modelData < 10 ? "0" + modelData : modelData
                font.pixelSize: 24
                font.weight: Font.DemiBold
                color: ListView.isCurrentItem ? "#000000" : "#999999"
                horizontalAlignment: Text.AlignHCenter
                verticalAlignment: Text.AlignVCenter
            }
        }
    }
}