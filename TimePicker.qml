import QtQuick 2.15
import QtQuick.Controls 2.15

Rectangle {
    id: root
    width: 220
    height: 120
    color: "#232325"

    property int hour: hourView.currentIndex
    property int minute: minuteView.currentIndex

    Row {
        anchors.centerIn: parent
        spacing: 8

        FlickableWheel {
            id: hourView
            width: 80
            height: 120
            model: 24
            delegate: Item {
                width: 80; height: 40
                Rectangle {
                    anchors.fill: parent
                    color: hourView.currentIndex === index ? "#f4f4f7" : "transparent"
                }
                Text {
                    anchors.centerIn: parent
                    text: modelData < 10 ? "0" + modelData : modelData
                    font.pixelSize: 32
                    color: hourView.currentIndex === index ? "white" : "#d1d1d6"
                }
            }
        }

        FlickableWheel {
            id: minuteView
            width: 80
            height: 120
            model: 60
            delegate: Item {
                width: 80; height: 40
                Rectangle {
                    anchors.fill: parent
                    color: minuteView.currentIndex === index ? "#f4f4f7" : "transparent"
                }
                Text {
                    anchors.centerIn: parent
                    text: modelData < 10 ? "0" + modelData : modelData
                    font.pixelSize: 32
                    color: minuteView.currentIndex === index ? "white" : "#d1d1d6"
                }
            }
        }
    }

    // 中间高亮线
    Rectangle {
        anchors.horizontalCenter: parent.horizontalCenter
        y: (root.height - 40) / 2
        width: root.width
        height: 40
        color: "transparent"
        border.color: "#ffffff22"
        border.width: 1
    }

    // 顶部和底部的渐隐遮罩
    Rectangle {
        anchors.top: parent.top
        width: parent.width
        height: 40
        z: 10
        gradient: Gradient {
            GradientStop { position: 0.0; color: "#232325" }
            GradientStop { position: 1.0; color: "#23232500" }
        }
    }

    Rectangle {
        anchors.bottom: parent.bottom
        width: parent.width
        height: 40
        z: 10
        gradient: Gradient {
            GradientStop { position: 0.0; color: "#23232500" }
            GradientStop { position: 1.0; color: "#232325" }
        }
    }
}