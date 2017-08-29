//
//  test_data.h
//  color_coding
//
//  Created by sheep on 2017/8/3.
//  Copyright © 2017年 sheep. All rights reserved.
//

#ifndef test_data_h
#define test_data_h

#include <stdio.h>

struct Graph* load_generate_tab_network();

struct Graph* load_hint_network();

struct MatrixDes* simpleTestMatrix();

void printMatrix(struct MatrixDes* md);

struct MatrixDes* generateTestMatrix(int ** mat, int length);

void freeMatrixDes(struct MatrixDes* md);

#endif /* test_data_h */
