//
//  basic.h
//  color_coding
//
//  Created by Yang Xu on 2017/8/16.
//  Copyright © 2017年 sheep. All rights reserved.
//

#ifndef basic_h
#define basic_h

#include <stdio.h>
#include "data_structure.h"

struct Graph* DiGraphFromMatrix(struct MatrixDes* md);

struct SubQueue* stronglyConnectedComponent(struct Graph* G);

#endif /* basic_h */
