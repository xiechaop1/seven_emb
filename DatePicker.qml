// DatePicker.qml
import QtQuick 2.15
import QtQuick.Controls 2.15

Rectangle {
    id: root
    width: 400
    height: 200
    color: "#18181a"

    property int startYear
    property int endYear
    property int year
    property int month
    property int day

    // 高亮区域
    Rectangle {
        anchors.horizontalCenter: parent.horizontalCenter
        y: (root.height - 40) / 2
        width: parent.width - 16
        height: 40
        color: "#585861"
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
            model: []
        }

        FlickableWheel {
            id: monthWheel
            width: 80
            height: 160
            model: ["1", "2", "3", "4", "5", "6",
                    "7", "8", "9", "10", "11", "12"]
        }

        FlickableWheel {
            id: dayWheel
            width: 80
            height: 160
            model: []
        }
    }

    // 顶部和底部渐隐
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

    // 初始化当前日期与模型
    Component.onCompleted: {
        let now = new Date()
        year = now.getFullYear()
        month = now.getMonth() + 1
        day = now.getDate()

        startYear = year - 10
        endYear = year + 10

        let years = []
        for (let y = startYear; y <= endYear; y++) {
            years.push(y.toString())
        }
        yearWheel.model = years
        yearWheel.currentIndex = year - startYear
        yearWheel.listView.positionViewAtIndex(yearWheel.currentIndex, ListView.Center)

        monthWheel.currentIndex = month - 1
        monthWheel.listView.positionViewAtIndex(monthWheel.currentIndex, ListView.Center)

        updateDays()
        dayWheel.currentIndex = day - 1
        dayWheel.listView.positionViewAtIndex(dayWheel.currentIndex, ListView.Center)
    }

    function updateDays() {
        let y = startYear + yearWheel.currentIndex
        let m = monthWheel.currentIndex + 1
        let daysInMonth = new Date(y, m, 0).getDate()
        let days = []
        for (let d = 1; d <= daysInMonth; d++) {
            days.push(d)
        }
        let oldIndex = dayWheel.currentIndex
        dayWheel.model = days
        if (oldIndex > days.length - 1) {
            dayWheel.currentIndex = days.length - 1
        } else {
            dayWheel.currentIndex = oldIndex
        }
        dayWheel.listView.positionViewAtIndex(dayWheel.currentIndex, ListView.Center)
    }

    Connections {
        target: yearWheel
        function onCurrentIndexChanged() {
            updateDays()
        }
    }
    Connections {
        target: monthWheel
        function onCurrentIndexChanged() {
            updateDays()
        }
    }

}