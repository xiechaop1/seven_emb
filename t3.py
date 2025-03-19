def run():
    time_duration = 1500  # ms
    sector_num = 8
    colors = [
        [255, 0, 0],
        [255, 3, 255],
        [15, 122, 255],
        [0, 222, 255],
        [3, 255, 3],
        [246, 255, 0],
        [255, 192, 0],
        [255, 96, 0]
    ]

    light_nums = [40, 32, 24, 16]
    light_sector_step = [
        5, 4, 3, 2
    ]

    sector_color_old = []
    # sector_buffer = []
    line_num = 4
    sector_area = []
    for idx in range(sector_num):
        sector_buffer = []
        first_num = 0
        for l_idx in range(line_num):

            if l_idx > 0:
                max_num = light_nums[l_idx - 1]
            else:
                max_num = 0

            first_num += max_num

            sector_start = first_num + light_sector_step[l_idx] * idx

            sector_buffer.append(sector_start)
        sector_area.append(sector_buffer)

    step = 0
    sector_pos = 0

    print(sector_area)
    # while True:
        # if self.light_mode != Code.LIGHT_MODE_SECTOR_FLOWING or self.ts > self.run_ts:
        #     break
    for _, color in enumerate(colors):

        sector_pos += step
        show_pos = sector_pos % sector_num

        sector = sector_area[show_pos]

        if show_pos < len(sector_color_old):
            old_color = sector_color_old[show_pos]
        else:
            old_color = [0, 0, 0]

        old_r, old_g, old_b = old_color
        curr_r, curr_g, curr_b = color

        # for one_idx, sector_one in enumerate(sector):
            # for one_idx in range(sector_one - 1):
            # self.fade(curr_r, curr_g, curr_b, old_r, old_g, old_b, sector_one, self.light_sector_step[one_idx])

    # time.sleep(time_duration / 1000)
    step += 1

run()