import QtQuick 2.15
import QtQuick.Controls 2.15

Rectangle {
    id: root
    width: 400
    height: 200
    color: "#18181a"

    property int currentYear: (new Date()).getFullYear()
    property int currentMonth: (new Date()).getMonth() + 1
    property int currentDay: (new Date()).getDate()
    property int startYear: currentYear - 10
    property int endYear: currentYear + 10

    property int year: yearWheel.currentIndex + startYear
    property int month: monthWheel.currentIndex + 1
    property int day: dayWheel.currentIndex + 1

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
            id: yearWheel
            width: 100
            height: 160
            model: endYear - startYear + 1
        }
        FlickableWheel {
            id: monthWheel
            width: 80
            height: 160
            model: [1,2,3,4,5,6,7,8,9,10,11,12]
        }
        FlickableWheel {
            id: dayWheel
            width: 80
            height: 160
            model: {
                var m = monthWheel.currentIndex + 1
                var y = yearWheel.currentIndex + startYear
                if (m === 2) {
                    if ((y % 4 === 0 && y % 100 !== 0) || (y % 400 === 0))
                        return 29
                    else
                        return 28
                }
                if ([1,3,5,7,8,10,12].indexOf(m) !== -1)
                    return 31
                return 30
            }
        }
    }

    // 默认选中当前日期
    Component.onCompleted: {
        yearWheel.currentIndex = currentYear - startYear
        monthWheel.currentIndex = currentMonth - 1
        dayWheel.currentIndex = currentDay - 1
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