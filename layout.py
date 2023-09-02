import numpy as np

def full_layout(x_boxes: int, y_boxes: int, fliplr:bool=False, flipud:bool=False, rotate_90=False):
    """ x_boxes: Number of Beer Crates horizontal
        y_boxes: Number of Beer Crates vertical"""
    layout =  np.array([[0, 9, 10, 19],
                             [1, 8, 11, 18],
                             [2, 7, 12, 17],
                             [3, 6, 13, 16],
                             [4, 5, 14, 15]])
    #We started with the vertical layout so the default is to rotate the box
    if not rotate_90:
        layout = np.rot90(layout, axes=(1,0))
    layout = np.fliplr(layout)
    matrix = layout

    if rotate_90:
        for x in range(1, x_boxes):
            layout = np.concatenate((layout, matrix+x*20), axis=1)
        for y in range(1, y_boxes):
            layout = np.concatenate((layout, layout+x_boxes*y*20), axis=0)
    else:
        for y in range(1, y_boxes):
            layout = np.concatenate((layout, matrix + y * 20), axis=0)
        matrix = layout
        for x in range(1, x_boxes):
            layout = np.concatenate((layout, matrix + y_boxes * x * 20), axis=1)

    if fliplr:
        layout = np.fliplr(layout)
    if flipud:
        layout = np.flipud(layout)
    return layout


if __name__ == '__main__':
    print('###If rotated boxes connect vertical###\n')
    print(full_layout(2,2, rotate_90=True))
    print(f'\n###fliplr rotates the layout on the y-axis###\n\n{full_layout(2, 2, rotate_90=True, fliplr=True)}')
    print('\n###If rotated boxes connect horizontal###\n\n')
    print(full_layout(3,2, rotate_90=False))
    print(f'\n###fliplr rotates the layout on the x-axis###\n\n{full_layout(2,2, rotate_90=False, flipud=True)}')


    print('\n### Example Layout with 5x3 boxes horizontal###\n')
    test = full_layout(5,3)
    print('\n'.join(['\t'.join([str(cell) for cell in row]) for row in test]))