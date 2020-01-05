Scaling segment lengths
=======================

.5      seems good for mobile/low res
.3 - .4 good for hi/res desktop

To run the scaling:

docker rm -f mesh && docker run -it --name mesh -v `pwd`:/models wearebeautiful/mesh /code/scale_mesh.py --len .2 /models/0003_VSA_MED_100pct__turned_90X.stl /models/0003-low-5.obj
