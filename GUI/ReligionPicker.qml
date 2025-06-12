import QtQuick 2.15
import QtQuick.Controls 2.15

Rectangle {
    id: root
    width: 400
    height: 200
    color: "#18181a"

    property int religionIndex: religionWheel.currentIndex
    property var religions: [
        "无宗教信仰", "佛教", "基督教", "伊斯兰教", "印度教", "道教", "其他"
    ]

    // 高亮区域
    Rectangle {
        anchors.horizontalCenter: parent.horizontalCenter
        y: (root.height - 40) / 2
        width: parent.width - 16   // 两边留8像素边距
        height: 40
        color: "#585861"  // 半透明淡灰色
        opacity: 0.2
        radius: 8
        z: 2
    }

    Row {
        anchors.centerIn: parent
        spacing: 16

        FlickableWheel {
            id: religionWheel
            width: 300
            height: 160
            model: religions
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