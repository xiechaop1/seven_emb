import QtQuick 2.15
import QtQuick.Controls 2.15

Rectangle {
    id: root
    width: 280  // 更宽
    height: 160 // 更高
    color: "#18181a"  // iOS风格背景

    property int hour: hourView.currentIndex
    property int minute: minuteView.currentIndex

    // 高亮区域
    Rectangle {
        anchors.horizontalCenter: parent.horizontalCenter
        y: (root.height - 40) / 2
        width: parent.width - 16   // 两边留8像素边距
        height: 40
        color: "#585861"  // 半透明淡灰色
        opacity: 0.8
        radius: 8
        z: 2
    }

    Row {
        anchors.fill: parent
        anchors.margins: 8  // 留边距
        spacing: 8

        FlickableWheel {
            id: hourView
            width: 120
            height: parent.height
            model: 24
        }
        FlickableWheel {
            id: minuteView
            width: 120
            height: parent.height
            model: 60
        }
    }

    // 顶部渐隐
    Rectangle {
        anchors.top: parent.top
        width: parent.width
        height: 32
        z: 10
        gradient: Gradient {
            GradientStop { position: 0.0; color: "#18181a" }
            GradientStop { position: 1.0; color: "#18181a00" }
        }
    }
    // 底部渐隐
    Rectangle {
        anchors.bottom: parent.bottom
        width: parent.width
        height: 32
        z: 10
        gradient: Gradient {
            GradientStop { position: 0.0; color: "#18181a00" }
            GradientStop { position: 1.0; color: "#18181a" }
        }
    }
}