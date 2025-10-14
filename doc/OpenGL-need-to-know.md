# Need to known for OpenGL

## glVertexAttribPointer

The glVertexAttribPointer function in OpenGL specifies the location and data format of the array of generic vertex attributes at index index to use when rendering.

Parameters:

- index: Specifies the index of the generic vertex attribute to be modified.
- size: Specifies the number of components per generic vertex attribute. Must be 1, 2, 3, or 4.
- type: Specifies the data type of each component in the array.
- normalized: Specifies whether fixed-point data values should be normalized.
- stride: Specifies the byte offset between consecutive generic vertex attributes.
- pointer: Specifies a pointer to the first component of the first generic vertex attribute in the array.

```cpp
// Enable the vertex attribute array for index 0
glEnableVertexAttribArray(0);

// Define an array of generic vertex attribute data
glVertexAttribPointer(
0, // attribute index
3, // number of components per vertex attribute
GL_FLOAT, // data type
GL_FALSE, // normalize flag
3 * sizeof(float), // stride
(void*)0 // offset
);
```
