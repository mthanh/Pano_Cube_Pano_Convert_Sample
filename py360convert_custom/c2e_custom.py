import numpy as np

from . import utils


def c2e_custom(cubemap, h, w, ratio_change, mode='bilinear', cube_format='dice'):
    if mode == 'bilinear':
        order = 1
    elif mode == 'nearest':
        order = 0
    else:
        raise NotImplementedError('unknown mode')

    if cube_format == 'horizon':
        pass
    elif cube_format == 'list':
        cubemap = utils.cube_list2h(cubemap)
    elif cube_format == 'dict':
        cubemap = utils.cube_dict2h(cubemap)
    elif cube_format == 'dice':
        cubemap = utils.cube_dice2h(cubemap)
    else:
        raise NotImplementedError('unknown cube_format')
    assert len(cubemap.shape) == 3
    assert cubemap.shape[0] * 6 == cubemap.shape[1]
    assert w % 8 == 0
    face_w = cubemap.shape[0]



    uv = utils.equirect_uvgrid(h, w)
    u, v = np.split(uv, 2, axis=-1)
    u = u[..., 0]
    v = v[..., 0]
    cube_faces = np.stack(np.split(cubemap, 6, 1), 0)


    # Get face id to each pixel: 0F 1R 2B 3L 4U 5D
    tp = utils.equirect_facetype(h, w)
    coor_x = np.zeros((h, w))
    coor_y = np.zeros((h, w))

    mask = (tp == 5)
    c = 0.5 * np.tan(np.pi / 2 - np.abs(v[mask]))
    coor_x[mask] = c * np.sin(u[mask])
    coor_y[mask] = -c * np.cos(u[mask])

    # Final renormalize
    coor_x = (np.clip(coor_x, -0.5, 0.5) + 0.5) * face_w
    coor_y = (np.clip(coor_y, -0.5, 0.5) + 0.5) * face_w

    # print(tp.shape)
    # print(coor_x.shape)
    # print(coor_y.shape)
    # print(cube_faces.shape)
    # print(order)
    #
    # # (5040, 6720)
    # # (5040, 6720)
    # # (5040, 6720)
    # # (6, 1680, 1680, 3)
    # # 1
    #
    # # return cubemap

    #crop for output size
    center_x = int(w/2)
    center_y = int(h*ratio_change)
    tp_cp = tp[center_y:, :]
    coor_x_cp = coor_x[center_y:, :]
    coor_y_cp = coor_y[center_y:, :]


    equirec = np.stack([
        # utils.sample_cubefaces_bottom(cube_faces[..., i], tp, coor_y, coor_x, order=order)
        utils.sample_cubefaces_bottom(cube_faces[..., i], tp_cp, coor_y_cp, coor_x_cp, order=order)
        for i in range(cube_faces.shape[3])
    ], axis=-1)

    return equirec
