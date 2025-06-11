import QtQuick 2.15
import QtQuick.Controls 2.15

Rectangle {
    width: 220; height: 120; color: "#232325"
    Row {
        anchors.centerIn: parent
        spacing: 8

        Wheel {
            id: hourWheel
            width: 80; height: 120
            model: 24
            currentIndex: 8
            delegate: Text {
                text: modelData < 10 ? "0" + modelData : modelData
                font.pixelSize: 32
                color: "#d1d1d6"
                horizontalAlignment: Text.AlignHCenter
                verticalAlignment: Text.AlignVCenter
            }
        }
        Wheel {
            id: minuteWheel
            width: 80; height: 120
            model: 60
            currentIndex: 0
            delegate: Text {
                text: modelData < 10 ? "0" + modelData : modelData
                font.pixelSize: 32
                color: "#d1d1d6"
                horizontalAlignment: Text.AlignHCenter
                verticalAlignment: Text.AlignVCenter
            }
        }
    }

    // 用于Python获取时间
    property int hour: hourWheel.currentIndex
    property int minute: minuteWheel.currentIndex
}