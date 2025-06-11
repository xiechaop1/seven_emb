import QtQuick 2.15
import QtQuick.Controls 2.15

Rectangle {
    id: root
    width: 220
    height: 120
    color: "#f2f2f7"  // 更接近 iOS 背景色

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
        }

        FlickableWheel {
            id: minuteView
            width: 80
            height: 120
            model: 60
        }
    }

    // 中间高亮区域
    Rectangle {
        anchors.horizontalCenter: parent.horizontalCenter
        y: (root.height - 40) / 2
        width: root.width
        height: 40
        color: "#ffffff44"  // 半透明白色，更符合 iOS 中线条
        radius: 4
        z: 2
    }

    // 顶部渐隐
    Rectangle {
        anchors.top: parent.top
        width: parent.width
        height: 30
        z: 10
        gradient: Gradient {
            GradientStop { position: 0.0; color: "#f2f2f7" }
            GradientStop { position: 1.0; color: "#f2f2f700" }
        }
    }

    // 底部渐隐
    Rectangle {
        anchors.bottom: parent.bottom
        width: parent.width
        height: 30
        z: 10
        gradient: Gradient {
            GradientStop { position: 0.0; color: "#f2f2f700" }
            GradientStop { position: 1.0; color: "#f2f2f7" }
        }
    }
}