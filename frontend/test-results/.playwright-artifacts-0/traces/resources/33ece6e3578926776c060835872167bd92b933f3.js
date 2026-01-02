(globalThis.TURBOPACK || (globalThis.TURBOPACK = [])).push([typeof document === "object" ? document.currentScript : undefined,
"[project]/node_modules/three/examples/jsm/utils/BufferGeometryUtils.js [app-client] (ecmascript)", ((__turbopack_context__) => {
"use strict";

__turbopack_context__.s([
    "computeMikkTSpaceTangents",
    ()=>computeMikkTSpaceTangents,
    "computeMorphedAttributes",
    ()=>computeMorphedAttributes,
    "deepCloneAttribute",
    ()=>deepCloneAttribute,
    "deinterleaveAttribute",
    ()=>deinterleaveAttribute,
    "deinterleaveGeometry",
    ()=>deinterleaveGeometry,
    "estimateBytesUsed",
    ()=>estimateBytesUsed,
    "interleaveAttributes",
    ()=>interleaveAttributes,
    "mergeAttributes",
    ()=>mergeAttributes,
    "mergeGeometries",
    ()=>mergeGeometries,
    "mergeGroups",
    ()=>mergeGroups,
    "mergeVertices",
    ()=>mergeVertices,
    "toCreasedNormals",
    ()=>toCreasedNormals,
    "toTrianglesDrawMode",
    ()=>toTrianglesDrawMode
]);
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$three$2f$build$2f$three$2e$core$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/node_modules/three/build/three.core.js [app-client] (ecmascript)");
;
/**
 * @module BufferGeometryUtils
 * @three_import import * as BufferGeometryUtils from 'three/addons/utils/BufferGeometryUtils.js';
 */ /**
 * Computes vertex tangents using the MikkTSpace algorithm. MikkTSpace generates the same tangents consistently,
 * and is used in most modelling tools and normal map bakers. Use MikkTSpace for materials with normal maps,
 * because inconsistent tangents may lead to subtle visual issues in the normal map, particularly around mirrored
 * UV seams.
 *
 * In comparison to this method, {@link BufferGeometry#computeTangents} (a custom algorithm) generates tangents that
 * probably will not match the tangents in other software. The custom algorithm is sufficient for general use with a
 * custom material, and may be faster than MikkTSpace.
 *
 * Returns the original BufferGeometry. Indexed geometries will be de-indexed. Requires position, normal, and uv attributes.
 *
 * @param {BufferGeometry} geometry - The geometry to compute tangents for.
 * @param {Object} MikkTSpace - Instance of `examples/jsm/libs/mikktspace.module.js`, or `mikktspace` npm package.
 * Await `MikkTSpace.ready` before use.
 * @param {boolean} [negateSign=true] - Whether to negate the sign component (.w) of each tangent.
 * Required for normal map conventions in some formats, including glTF.
 * @return {BufferGeometry} The updated geometry.
 */ function computeMikkTSpaceTangents(geometry, MikkTSpace, negateSign = true) {
    if (!MikkTSpace || !MikkTSpace.isReady) {
        throw new Error('BufferGeometryUtils: Initialized MikkTSpace library required.');
    }
    if (!geometry.hasAttribute('position') || !geometry.hasAttribute('normal') || !geometry.hasAttribute('uv')) {
        throw new Error('BufferGeometryUtils: Tangents require "position", "normal", and "uv" attributes.');
    }
    function getAttributeArray(attribute) {
        if (attribute.normalized || attribute.isInterleavedBufferAttribute) {
            const dstArray = new Float32Array(attribute.count * attribute.itemSize);
            for(let i = 0, j = 0; i < attribute.count; i++){
                dstArray[j++] = attribute.getX(i);
                dstArray[j++] = attribute.getY(i);
                if (attribute.itemSize > 2) {
                    dstArray[j++] = attribute.getZ(i);
                }
            }
            return dstArray;
        }
        if (attribute.array instanceof Float32Array) {
            return attribute.array;
        }
        return new Float32Array(attribute.array);
    }
    // MikkTSpace algorithm requires non-indexed input.
    const _geometry = geometry.index ? geometry.toNonIndexed() : geometry;
    // Compute vertex tangents.
    const tangents = MikkTSpace.generateTangents(getAttributeArray(_geometry.attributes.position), getAttributeArray(_geometry.attributes.normal), getAttributeArray(_geometry.attributes.uv));
    // Texture coordinate convention of glTF differs from the apparent
    // default of the MikkTSpace library; .w component must be flipped.
    if (negateSign) {
        for(let i = 3; i < tangents.length; i += 4){
            tangents[i] *= -1;
        }
    }
    //
    _geometry.setAttribute('tangent', new __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$three$2f$build$2f$three$2e$core$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["BufferAttribute"](tangents, 4));
    if (geometry !== _geometry) {
        geometry.copy(_geometry);
    }
    return geometry;
}
/**
 * Merges a set of geometries into a single instance. All geometries must have compatible attributes.
 *
 * @param {Array<BufferGeometry>} geometries - The geometries to merge.
 * @param {boolean} [useGroups=false] - Whether to use groups or not.
 * @return {?BufferGeometry} The merged geometry. Returns `null` if the merge does not succeed.
 */ function mergeGeometries(geometries, useGroups = false) {
    const isIndexed = geometries[0].index !== null;
    const attributesUsed = new Set(Object.keys(geometries[0].attributes));
    const morphAttributesUsed = new Set(Object.keys(geometries[0].morphAttributes));
    const attributes = {};
    const morphAttributes = {};
    const morphTargetsRelative = geometries[0].morphTargetsRelative;
    const mergedGeometry = new __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$three$2f$build$2f$three$2e$core$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["BufferGeometry"]();
    let offset = 0;
    for(let i = 0; i < geometries.length; ++i){
        const geometry = geometries[i];
        let attributesCount = 0;
        // ensure that all geometries are indexed, or none
        if (isIndexed !== (geometry.index !== null)) {
            console.error('THREE.BufferGeometryUtils: .mergeGeometries() failed with geometry at index ' + i + '. All geometries must have compatible attributes; make sure index attribute exists among all geometries, or in none of them.');
            return null;
        }
        // gather attributes, exit early if they're different
        for(const name in geometry.attributes){
            if (!attributesUsed.has(name)) {
                console.error('THREE.BufferGeometryUtils: .mergeGeometries() failed with geometry at index ' + i + '. All geometries must have compatible attributes; make sure "' + name + '" attribute exists among all geometries, or in none of them.');
                return null;
            }
            if (attributes[name] === undefined) attributes[name] = [];
            attributes[name].push(geometry.attributes[name]);
            attributesCount++;
        }
        // ensure geometries have the same number of attributes
        if (attributesCount !== attributesUsed.size) {
            console.error('THREE.BufferGeometryUtils: .mergeGeometries() failed with geometry at index ' + i + '. Make sure all geometries have the same number of attributes.');
            return null;
        }
        // gather morph attributes, exit early if they're different
        if (morphTargetsRelative !== geometry.morphTargetsRelative) {
            console.error('THREE.BufferGeometryUtils: .mergeGeometries() failed with geometry at index ' + i + '. .morphTargetsRelative must be consistent throughout all geometries.');
            return null;
        }
        for(const name in geometry.morphAttributes){
            if (!morphAttributesUsed.has(name)) {
                console.error('THREE.BufferGeometryUtils: .mergeGeometries() failed with geometry at index ' + i + '.  .morphAttributes must be consistent throughout all geometries.');
                return null;
            }
            if (morphAttributes[name] === undefined) morphAttributes[name] = [];
            morphAttributes[name].push(geometry.morphAttributes[name]);
        }
        if (useGroups) {
            let count;
            if (isIndexed) {
                count = geometry.index.count;
            } else if (geometry.attributes.position !== undefined) {
                count = geometry.attributes.position.count;
            } else {
                console.error('THREE.BufferGeometryUtils: .mergeGeometries() failed with geometry at index ' + i + '. The geometry must have either an index or a position attribute');
                return null;
            }
            mergedGeometry.addGroup(offset, count, i);
            offset += count;
        }
    }
    // merge indices
    if (isIndexed) {
        let indexOffset = 0;
        const mergedIndex = [];
        for(let i = 0; i < geometries.length; ++i){
            const index = geometries[i].index;
            for(let j = 0; j < index.count; ++j){
                mergedIndex.push(index.getX(j) + indexOffset);
            }
            indexOffset += geometries[i].attributes.position.count;
        }
        mergedGeometry.setIndex(mergedIndex);
    }
    // merge attributes
    for(const name in attributes){
        const mergedAttribute = mergeAttributes(attributes[name]);
        if (!mergedAttribute) {
            console.error('THREE.BufferGeometryUtils: .mergeGeometries() failed while trying to merge the ' + name + ' attribute.');
            return null;
        }
        mergedGeometry.setAttribute(name, mergedAttribute);
    }
    // merge morph attributes
    for(const name in morphAttributes){
        const numMorphTargets = morphAttributes[name][0].length;
        if (numMorphTargets === 0) break;
        mergedGeometry.morphAttributes = mergedGeometry.morphAttributes || {};
        mergedGeometry.morphAttributes[name] = [];
        for(let i = 0; i < numMorphTargets; ++i){
            const morphAttributesToMerge = [];
            for(let j = 0; j < morphAttributes[name].length; ++j){
                morphAttributesToMerge.push(morphAttributes[name][j][i]);
            }
            const mergedMorphAttribute = mergeAttributes(morphAttributesToMerge);
            if (!mergedMorphAttribute) {
                console.error('THREE.BufferGeometryUtils: .mergeGeometries() failed while trying to merge the ' + name + ' morphAttribute.');
                return null;
            }
            mergedGeometry.morphAttributes[name].push(mergedMorphAttribute);
        }
    }
    return mergedGeometry;
}
/**
 * Merges a set of attributes into a single instance. All attributes must have compatible properties and types.
 * Instances of {@link InterleavedBufferAttribute} are not supported.
 *
 * @param {Array<BufferAttribute>} attributes - The attributes to merge.
 * @return {?BufferAttribute} The merged attribute. Returns `null` if the merge does not succeed.
 */ function mergeAttributes(attributes) {
    let TypedArray;
    let itemSize;
    let normalized;
    let gpuType = -1;
    let arrayLength = 0;
    for(let i = 0; i < attributes.length; ++i){
        const attribute = attributes[i];
        if (TypedArray === undefined) TypedArray = attribute.array.constructor;
        if (TypedArray !== attribute.array.constructor) {
            console.error('THREE.BufferGeometryUtils: .mergeAttributes() failed. BufferAttribute.array must be of consistent array types across matching attributes.');
            return null;
        }
        if (itemSize === undefined) itemSize = attribute.itemSize;
        if (itemSize !== attribute.itemSize) {
            console.error('THREE.BufferGeometryUtils: .mergeAttributes() failed. BufferAttribute.itemSize must be consistent across matching attributes.');
            return null;
        }
        if (normalized === undefined) normalized = attribute.normalized;
        if (normalized !== attribute.normalized) {
            console.error('THREE.BufferGeometryUtils: .mergeAttributes() failed. BufferAttribute.normalized must be consistent across matching attributes.');
            return null;
        }
        if (gpuType === -1) gpuType = attribute.gpuType;
        if (gpuType !== attribute.gpuType) {
            console.error('THREE.BufferGeometryUtils: .mergeAttributes() failed. BufferAttribute.gpuType must be consistent across matching attributes.');
            return null;
        }
        arrayLength += attribute.count * itemSize;
    }
    const array = new TypedArray(arrayLength);
    const result = new __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$three$2f$build$2f$three$2e$core$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["BufferAttribute"](array, itemSize, normalized);
    let offset = 0;
    for(let i = 0; i < attributes.length; ++i){
        const attribute = attributes[i];
        if (attribute.isInterleavedBufferAttribute) {
            const tupleOffset = offset / itemSize;
            for(let j = 0, l = attribute.count; j < l; j++){
                for(let c = 0; c < itemSize; c++){
                    const value = attribute.getComponent(j, c);
                    result.setComponent(j + tupleOffset, c, value);
                }
            }
        } else {
            array.set(attribute.array, offset);
        }
        offset += attribute.count * itemSize;
    }
    if (gpuType !== undefined) {
        result.gpuType = gpuType;
    }
    return result;
}
/**
 * Performs a deep clone of the given buffer attribute.
 *
 * @param {BufferAttribute} attribute - The attribute to clone.
 * @return {BufferAttribute} The cloned attribute.
 */ function deepCloneAttribute(attribute) {
    if (attribute.isInstancedInterleavedBufferAttribute || attribute.isInterleavedBufferAttribute) {
        return deinterleaveAttribute(attribute);
    }
    if (attribute.isInstancedBufferAttribute) {
        return new __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$three$2f$build$2f$three$2e$core$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["InstancedBufferAttribute"]().copy(attribute);
    }
    return new __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$three$2f$build$2f$three$2e$core$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["BufferAttribute"]().copy(attribute);
}
/**
 * Interleaves a set of attributes and returns a new array of corresponding attributes that share a
 * single {@link InterleavedBuffer} instance. All attributes must have compatible types.
 *
 * @param {Array<BufferAttribute>} attributes - The attributes to interleave.
 * @return {?Array<InterleavedBufferAttribute>} An array of interleaved attributes. If interleave does not succeed, the method returns `null`.
 */ function interleaveAttributes(attributes) {
    // Interleaves the provided attributes into an InterleavedBuffer and returns
    // a set of InterleavedBufferAttributes for each attribute
    let TypedArray;
    let arrayLength = 0;
    let stride = 0;
    // calculate the length and type of the interleavedBuffer
    for(let i = 0, l = attributes.length; i < l; ++i){
        const attribute = attributes[i];
        if (TypedArray === undefined) TypedArray = attribute.array.constructor;
        if (TypedArray !== attribute.array.constructor) {
            console.error('AttributeBuffers of different types cannot be interleaved');
            return null;
        }
        arrayLength += attribute.array.length;
        stride += attribute.itemSize;
    }
    // Create the set of buffer attributes
    const interleavedBuffer = new __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$three$2f$build$2f$three$2e$core$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["InterleavedBuffer"](new TypedArray(arrayLength), stride);
    let offset = 0;
    const res = [];
    const getters = [
        'getX',
        'getY',
        'getZ',
        'getW'
    ];
    const setters = [
        'setX',
        'setY',
        'setZ',
        'setW'
    ];
    for(let j = 0, l = attributes.length; j < l; j++){
        const attribute = attributes[j];
        const itemSize = attribute.itemSize;
        const count = attribute.count;
        const iba = new __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$three$2f$build$2f$three$2e$core$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["InterleavedBufferAttribute"](interleavedBuffer, itemSize, offset, attribute.normalized);
        res.push(iba);
        offset += itemSize;
        // Move the data for each attribute into the new interleavedBuffer
        // at the appropriate offset
        for(let c = 0; c < count; c++){
            for(let k = 0; k < itemSize; k++){
                iba[setters[k]](c, attribute[getters[k]](c));
            }
        }
    }
    return res;
}
/**
 * Returns a new, non-interleaved version of the given attribute.
 *
 * @param {InterleavedBufferAttribute} attribute - The interleaved attribute.
 * @return {BufferAttribute} The non-interleaved attribute.
 */ function deinterleaveAttribute(attribute) {
    const cons = attribute.data.array.constructor;
    const count = attribute.count;
    const itemSize = attribute.itemSize;
    const normalized = attribute.normalized;
    const array = new cons(count * itemSize);
    let newAttribute;
    if (attribute.isInstancedInterleavedBufferAttribute) {
        newAttribute = new __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$three$2f$build$2f$three$2e$core$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["InstancedBufferAttribute"](array, itemSize, normalized, attribute.meshPerAttribute);
    } else {
        newAttribute = new __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$three$2f$build$2f$three$2e$core$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["BufferAttribute"](array, itemSize, normalized);
    }
    for(let i = 0; i < count; i++){
        newAttribute.setX(i, attribute.getX(i));
        if (itemSize >= 2) {
            newAttribute.setY(i, attribute.getY(i));
        }
        if (itemSize >= 3) {
            newAttribute.setZ(i, attribute.getZ(i));
        }
        if (itemSize >= 4) {
            newAttribute.setW(i, attribute.getW(i));
        }
    }
    return newAttribute;
}
/**
 * Deinterleaves all attributes on the given geometry.
 *
 * @param {BufferGeometry} geometry - The geometry to deinterleave.
 */ function deinterleaveGeometry(geometry) {
    const attributes = geometry.attributes;
    const morphTargets = geometry.morphTargets;
    const attrMap = new Map();
    for(const key in attributes){
        const attr = attributes[key];
        if (attr.isInterleavedBufferAttribute) {
            if (!attrMap.has(attr)) {
                attrMap.set(attr, deinterleaveAttribute(attr));
            }
            attributes[key] = attrMap.get(attr);
        }
    }
    for(const key in morphTargets){
        const attr = morphTargets[key];
        if (attr.isInterleavedBufferAttribute) {
            if (!attrMap.has(attr)) {
                attrMap.set(attr, deinterleaveAttribute(attr));
            }
            morphTargets[key] = attrMap.get(attr);
        }
    }
}
/**
 * Returns the amount of bytes used by all attributes to represent the geometry.
 *
 * @param {BufferGeometry} geometry - The geometry.
 * @return {number} The estimate bytes used.
 */ function estimateBytesUsed(geometry) {
    // Return the estimated memory used by this geometry in bytes
    // Calculate using itemSize, count, and BYTES_PER_ELEMENT to account
    // for InterleavedBufferAttributes.
    let mem = 0;
    for(const name in geometry.attributes){
        const attr = geometry.getAttribute(name);
        mem += attr.count * attr.itemSize * attr.array.BYTES_PER_ELEMENT;
    }
    const indices = geometry.getIndex();
    mem += indices ? indices.count * indices.itemSize * indices.array.BYTES_PER_ELEMENT : 0;
    return mem;
}
/**
 * Returns a new geometry with vertices for which all similar vertex attributes (within tolerance) are merged.
 *
 * @param {BufferGeometry} geometry - The geometry to merge vertices for.
 * @param {number} [tolerance=1e-4] - The tolerance value.
 * @return {BufferGeometry} - The new geometry with merged vertices.
 */ function mergeVertices(geometry, tolerance = 1e-4) {
    tolerance = Math.max(tolerance, Number.EPSILON);
    // Generate an index buffer if the geometry doesn't have one, or optimize it
    // if it's already available.
    const hashToIndex = {};
    const indices = geometry.getIndex();
    const positions = geometry.getAttribute('position');
    const vertexCount = indices ? indices.count : positions.count;
    // next value for triangle indices
    let nextIndex = 0;
    // attributes and new attribute arrays
    const attributeNames = Object.keys(geometry.attributes);
    const tmpAttributes = {};
    const tmpMorphAttributes = {};
    const newIndices = [];
    const getters = [
        'getX',
        'getY',
        'getZ',
        'getW'
    ];
    const setters = [
        'setX',
        'setY',
        'setZ',
        'setW'
    ];
    // Initialize the arrays, allocating space conservatively. Extra
    // space will be trimmed in the last step.
    for(let i = 0, l = attributeNames.length; i < l; i++){
        const name = attributeNames[i];
        const attr = geometry.attributes[name];
        tmpAttributes[name] = new attr.constructor(new attr.array.constructor(attr.count * attr.itemSize), attr.itemSize, attr.normalized);
        const morphAttributes = geometry.morphAttributes[name];
        if (morphAttributes) {
            if (!tmpMorphAttributes[name]) tmpMorphAttributes[name] = [];
            morphAttributes.forEach((morphAttr, i)=>{
                const array = new morphAttr.array.constructor(morphAttr.count * morphAttr.itemSize);
                tmpMorphAttributes[name][i] = new morphAttr.constructor(array, morphAttr.itemSize, morphAttr.normalized);
            });
        }
    }
    // convert the error tolerance to an amount of decimal places to truncate to
    const halfTolerance = tolerance * 0.5;
    const exponent = Math.log10(1 / tolerance);
    const hashMultiplier = Math.pow(10, exponent);
    const hashAdditive = halfTolerance * hashMultiplier;
    for(let i = 0; i < vertexCount; i++){
        const index = indices ? indices.getX(i) : i;
        // Generate a hash for the vertex attributes at the current index 'i'
        let hash = '';
        for(let j = 0, l = attributeNames.length; j < l; j++){
            const name = attributeNames[j];
            const attribute = geometry.getAttribute(name);
            const itemSize = attribute.itemSize;
            for(let k = 0; k < itemSize; k++){
                // double tilde truncates the decimal value
                hash += `${~~(attribute[getters[k]](index) * hashMultiplier + hashAdditive)},`;
            }
        }
        // Add another reference to the vertex if it's already
        // used by another index
        if (hash in hashToIndex) {
            newIndices.push(hashToIndex[hash]);
        } else {
            // copy data to the new index in the temporary attributes
            for(let j = 0, l = attributeNames.length; j < l; j++){
                const name = attributeNames[j];
                const attribute = geometry.getAttribute(name);
                const morphAttributes = geometry.morphAttributes[name];
                const itemSize = attribute.itemSize;
                const newArray = tmpAttributes[name];
                const newMorphArrays = tmpMorphAttributes[name];
                for(let k = 0; k < itemSize; k++){
                    const getterFunc = getters[k];
                    const setterFunc = setters[k];
                    newArray[setterFunc](nextIndex, attribute[getterFunc](index));
                    if (morphAttributes) {
                        for(let m = 0, ml = morphAttributes.length; m < ml; m++){
                            newMorphArrays[m][setterFunc](nextIndex, morphAttributes[m][getterFunc](index));
                        }
                    }
                }
            }
            hashToIndex[hash] = nextIndex;
            newIndices.push(nextIndex);
            nextIndex++;
        }
    }
    // generate result BufferGeometry
    const result = geometry.clone();
    for(const name in geometry.attributes){
        const tmpAttribute = tmpAttributes[name];
        result.setAttribute(name, new tmpAttribute.constructor(tmpAttribute.array.slice(0, nextIndex * tmpAttribute.itemSize), tmpAttribute.itemSize, tmpAttribute.normalized));
        if (!(name in tmpMorphAttributes)) continue;
        for(let j = 0; j < tmpMorphAttributes[name].length; j++){
            const tmpMorphAttribute = tmpMorphAttributes[name][j];
            result.morphAttributes[name][j] = new tmpMorphAttribute.constructor(tmpMorphAttribute.array.slice(0, nextIndex * tmpMorphAttribute.itemSize), tmpMorphAttribute.itemSize, tmpMorphAttribute.normalized);
        }
    }
    // indices
    result.setIndex(newIndices);
    return result;
}
/**
 * Returns a new indexed geometry based on `TrianglesDrawMode` draw mode.
 * This mode corresponds to the `gl.TRIANGLES` primitive in WebGL.
 *
 * @param {BufferGeometry} geometry - The geometry to convert.
 * @param {number} drawMode - The current draw mode.
 * @return {BufferGeometry} The new geometry using `TrianglesDrawMode`.
 */ function toTrianglesDrawMode(geometry, drawMode) {
    if (drawMode === __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$three$2f$build$2f$three$2e$core$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["TrianglesDrawMode"]) {
        console.warn('THREE.BufferGeometryUtils.toTrianglesDrawMode(): Geometry already defined as triangles.');
        return geometry;
    }
    if (drawMode === __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$three$2f$build$2f$three$2e$core$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["TriangleFanDrawMode"] || drawMode === __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$three$2f$build$2f$three$2e$core$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["TriangleStripDrawMode"]) {
        let index = geometry.getIndex();
        // generate index if not present
        if (index === null) {
            const indices = [];
            const position = geometry.getAttribute('position');
            if (position !== undefined) {
                for(let i = 0; i < position.count; i++){
                    indices.push(i);
                }
                geometry.setIndex(indices);
                index = geometry.getIndex();
            } else {
                console.error('THREE.BufferGeometryUtils.toTrianglesDrawMode(): Undefined position attribute. Processing not possible.');
                return geometry;
            }
        }
        //
        const numberOfTriangles = index.count - 2;
        const newIndices = [];
        if (drawMode === __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$three$2f$build$2f$three$2e$core$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["TriangleFanDrawMode"]) {
            // gl.TRIANGLE_FAN
            for(let i = 1; i <= numberOfTriangles; i++){
                newIndices.push(index.getX(0));
                newIndices.push(index.getX(i));
                newIndices.push(index.getX(i + 1));
            }
        } else {
            // gl.TRIANGLE_STRIP
            for(let i = 0; i < numberOfTriangles; i++){
                if (i % 2 === 0) {
                    newIndices.push(index.getX(i));
                    newIndices.push(index.getX(i + 1));
                    newIndices.push(index.getX(i + 2));
                } else {
                    newIndices.push(index.getX(i + 2));
                    newIndices.push(index.getX(i + 1));
                    newIndices.push(index.getX(i));
                }
            }
        }
        if (newIndices.length / 3 !== numberOfTriangles) {
            console.error('THREE.BufferGeometryUtils.toTrianglesDrawMode(): Unable to generate correct amount of triangles.');
        }
        // build final geometry
        const newGeometry = geometry.clone();
        newGeometry.setIndex(newIndices);
        newGeometry.clearGroups();
        return newGeometry;
    } else {
        console.error('THREE.BufferGeometryUtils.toTrianglesDrawMode(): Unknown draw mode:', drawMode);
        return geometry;
    }
}
/**
 * Calculates the morphed attributes of a morphed/skinned BufferGeometry.
 *
 * Helpful for Raytracing or Decals (i.e. a `DecalGeometry` applied to a morphed Object with a `BufferGeometry`
 * will use the original `BufferGeometry`, not the morphed/skinned one, generating an incorrect result.
 * Using this function to create a shadow `Object3`D the `DecalGeometry` can be correctly generated).
 *
 * @param {Mesh|Line|Points} object - The 3D object to compute morph attributes for.
 * @return {Object} An object with original position/normal attributes and morphed ones.
 */ function computeMorphedAttributes(object) {
    const _vA = new __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$three$2f$build$2f$three$2e$core$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["Vector3"]();
    const _vB = new __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$three$2f$build$2f$three$2e$core$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["Vector3"]();
    const _vC = new __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$three$2f$build$2f$three$2e$core$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["Vector3"]();
    const _tempA = new __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$three$2f$build$2f$three$2e$core$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["Vector3"]();
    const _tempB = new __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$three$2f$build$2f$three$2e$core$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["Vector3"]();
    const _tempC = new __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$three$2f$build$2f$three$2e$core$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["Vector3"]();
    const _morphA = new __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$three$2f$build$2f$three$2e$core$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["Vector3"]();
    const _morphB = new __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$three$2f$build$2f$three$2e$core$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["Vector3"]();
    const _morphC = new __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$three$2f$build$2f$three$2e$core$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["Vector3"]();
    function _calculateMorphedAttributeData(object, attribute, morphAttribute, morphTargetsRelative, a, b, c, modifiedAttributeArray) {
        _vA.fromBufferAttribute(attribute, a);
        _vB.fromBufferAttribute(attribute, b);
        _vC.fromBufferAttribute(attribute, c);
        const morphInfluences = object.morphTargetInfluences;
        if (morphAttribute && morphInfluences) {
            _morphA.set(0, 0, 0);
            _morphB.set(0, 0, 0);
            _morphC.set(0, 0, 0);
            for(let i = 0, il = morphAttribute.length; i < il; i++){
                const influence = morphInfluences[i];
                const morph = morphAttribute[i];
                if (influence === 0) continue;
                _tempA.fromBufferAttribute(morph, a);
                _tempB.fromBufferAttribute(morph, b);
                _tempC.fromBufferAttribute(morph, c);
                if (morphTargetsRelative) {
                    _morphA.addScaledVector(_tempA, influence);
                    _morphB.addScaledVector(_tempB, influence);
                    _morphC.addScaledVector(_tempC, influence);
                } else {
                    _morphA.addScaledVector(_tempA.sub(_vA), influence);
                    _morphB.addScaledVector(_tempB.sub(_vB), influence);
                    _morphC.addScaledVector(_tempC.sub(_vC), influence);
                }
            }
            _vA.add(_morphA);
            _vB.add(_morphB);
            _vC.add(_morphC);
        }
        if (object.isSkinnedMesh) {
            object.applyBoneTransform(a, _vA);
            object.applyBoneTransform(b, _vB);
            object.applyBoneTransform(c, _vC);
        }
        modifiedAttributeArray[a * 3 + 0] = _vA.x;
        modifiedAttributeArray[a * 3 + 1] = _vA.y;
        modifiedAttributeArray[a * 3 + 2] = _vA.z;
        modifiedAttributeArray[b * 3 + 0] = _vB.x;
        modifiedAttributeArray[b * 3 + 1] = _vB.y;
        modifiedAttributeArray[b * 3 + 2] = _vB.z;
        modifiedAttributeArray[c * 3 + 0] = _vC.x;
        modifiedAttributeArray[c * 3 + 1] = _vC.y;
        modifiedAttributeArray[c * 3 + 2] = _vC.z;
    }
    const geometry = object.geometry;
    const material = object.material;
    let a, b, c;
    const index = geometry.index;
    const positionAttribute = geometry.attributes.position;
    const morphPosition = geometry.morphAttributes.position;
    const morphTargetsRelative = geometry.morphTargetsRelative;
    const normalAttribute = geometry.attributes.normal;
    const morphNormal = geometry.morphAttributes.position;
    const groups = geometry.groups;
    const drawRange = geometry.drawRange;
    let i, j, il, jl;
    let group;
    let start, end;
    const modifiedPosition = new Float32Array(positionAttribute.count * positionAttribute.itemSize);
    const modifiedNormal = new Float32Array(normalAttribute.count * normalAttribute.itemSize);
    if (index !== null) {
        // indexed buffer geometry
        if (Array.isArray(material)) {
            for(i = 0, il = groups.length; i < il; i++){
                group = groups[i];
                start = Math.max(group.start, drawRange.start);
                end = Math.min(group.start + group.count, drawRange.start + drawRange.count);
                for(j = start, jl = end; j < jl; j += 3){
                    a = index.getX(j);
                    b = index.getX(j + 1);
                    c = index.getX(j + 2);
                    _calculateMorphedAttributeData(object, positionAttribute, morphPosition, morphTargetsRelative, a, b, c, modifiedPosition);
                    _calculateMorphedAttributeData(object, normalAttribute, morphNormal, morphTargetsRelative, a, b, c, modifiedNormal);
                }
            }
        } else {
            start = Math.max(0, drawRange.start);
            end = Math.min(index.count, drawRange.start + drawRange.count);
            for(i = start, il = end; i < il; i += 3){
                a = index.getX(i);
                b = index.getX(i + 1);
                c = index.getX(i + 2);
                _calculateMorphedAttributeData(object, positionAttribute, morphPosition, morphTargetsRelative, a, b, c, modifiedPosition);
                _calculateMorphedAttributeData(object, normalAttribute, morphNormal, morphTargetsRelative, a, b, c, modifiedNormal);
            }
        }
    } else {
        // non-indexed buffer geometry
        if (Array.isArray(material)) {
            for(i = 0, il = groups.length; i < il; i++){
                group = groups[i];
                start = Math.max(group.start, drawRange.start);
                end = Math.min(group.start + group.count, drawRange.start + drawRange.count);
                for(j = start, jl = end; j < jl; j += 3){
                    a = j;
                    b = j + 1;
                    c = j + 2;
                    _calculateMorphedAttributeData(object, positionAttribute, morphPosition, morphTargetsRelative, a, b, c, modifiedPosition);
                    _calculateMorphedAttributeData(object, normalAttribute, morphNormal, morphTargetsRelative, a, b, c, modifiedNormal);
                }
            }
        } else {
            start = Math.max(0, drawRange.start);
            end = Math.min(positionAttribute.count, drawRange.start + drawRange.count);
            for(i = start, il = end; i < il; i += 3){
                a = i;
                b = i + 1;
                c = i + 2;
                _calculateMorphedAttributeData(object, positionAttribute, morphPosition, morphTargetsRelative, a, b, c, modifiedPosition);
                _calculateMorphedAttributeData(object, normalAttribute, morphNormal, morphTargetsRelative, a, b, c, modifiedNormal);
            }
        }
    }
    const morphedPositionAttribute = new __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$three$2f$build$2f$three$2e$core$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["Float32BufferAttribute"](modifiedPosition, 3);
    const morphedNormalAttribute = new __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$three$2f$build$2f$three$2e$core$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["Float32BufferAttribute"](modifiedNormal, 3);
    return {
        positionAttribute: positionAttribute,
        normalAttribute: normalAttribute,
        morphedPositionAttribute: morphedPositionAttribute,
        morphedNormalAttribute: morphedNormalAttribute
    };
}
/**
 * Merges the {@link BufferGeometry#groups} for the given geometry.
 *
 * @param {BufferGeometry} geometry - The geometry to modify.
 * @return {BufferGeometry} - The updated geometry
 */ function mergeGroups(geometry) {
    if (geometry.groups.length === 0) {
        console.warn('THREE.BufferGeometryUtils.mergeGroups(): No groups are defined. Nothing to merge.');
        return geometry;
    }
    let groups = geometry.groups;
    // sort groups by material index
    groups = groups.sort((a, b)=>{
        if (a.materialIndex !== b.materialIndex) return a.materialIndex - b.materialIndex;
        return a.start - b.start;
    });
    // create index for non-indexed geometries
    if (geometry.getIndex() === null) {
        const positionAttribute = geometry.getAttribute('position');
        const indices = [];
        for(let i = 0; i < positionAttribute.count; i += 3){
            indices.push(i, i + 1, i + 2);
        }
        geometry.setIndex(indices);
    }
    // sort index
    const index = geometry.getIndex();
    const newIndices = [];
    for(let i = 0; i < groups.length; i++){
        const group = groups[i];
        const groupStart = group.start;
        const groupLength = groupStart + group.count;
        for(let j = groupStart; j < groupLength; j++){
            newIndices.push(index.getX(j));
        }
    }
    geometry.dispose(); // Required to force buffer recreation
    geometry.setIndex(newIndices);
    // update groups indices
    let start = 0;
    for(let i = 0; i < groups.length; i++){
        const group = groups[i];
        group.start = start;
        start += group.count;
    }
    // merge groups
    let currentGroup = groups[0];
    geometry.groups = [
        currentGroup
    ];
    for(let i = 1; i < groups.length; i++){
        const group = groups[i];
        if (currentGroup.materialIndex === group.materialIndex) {
            currentGroup.count += group.count;
        } else {
            currentGroup = group;
            geometry.groups.push(currentGroup);
        }
    }
    return geometry;
}
/**
 * Modifies the supplied geometry if it is non-indexed, otherwise creates a new,
 * non-indexed geometry. Returns the geometry with smooth normals everywhere except
 * faces that meet at an angle greater than the crease angle.
 *
 * @param {BufferGeometry} geometry - The geometry to modify.
 * @param {number} [creaseAngle=Math.PI/3] - The crease angle in radians.
 * @return {BufferGeometry} - The updated geometry
 */ function toCreasedNormals(geometry, creaseAngle = Math.PI / 3 /* 60 degrees */ ) {
    const creaseDot = Math.cos(creaseAngle);
    const hashMultiplier = (1 + 1e-10) * 1e2;
    // reusable vectors
    const verts = [
        new __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$three$2f$build$2f$three$2e$core$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["Vector3"](),
        new __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$three$2f$build$2f$three$2e$core$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["Vector3"](),
        new __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$three$2f$build$2f$three$2e$core$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["Vector3"]()
    ];
    const tempVec1 = new __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$three$2f$build$2f$three$2e$core$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["Vector3"]();
    const tempVec2 = new __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$three$2f$build$2f$three$2e$core$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["Vector3"]();
    const tempNorm = new __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$three$2f$build$2f$three$2e$core$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["Vector3"]();
    const tempNorm2 = new __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$three$2f$build$2f$three$2e$core$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["Vector3"]();
    // hashes a vector
    function hashVertex(v) {
        const x = ~~(v.x * hashMultiplier);
        const y = ~~(v.y * hashMultiplier);
        const z = ~~(v.z * hashMultiplier);
        return `${x},${y},${z}`;
    }
    // BufferGeometry.toNonIndexed() warns if the geometry is non-indexed
    // and returns the original geometry
    const resultGeometry = geometry.index ? geometry.toNonIndexed() : geometry;
    const posAttr = resultGeometry.attributes.position;
    const vertexMap = {};
    // find all the normals shared by commonly located vertices
    for(let i = 0, l = posAttr.count / 3; i < l; i++){
        const i3 = 3 * i;
        const a = verts[0].fromBufferAttribute(posAttr, i3 + 0);
        const b = verts[1].fromBufferAttribute(posAttr, i3 + 1);
        const c = verts[2].fromBufferAttribute(posAttr, i3 + 2);
        tempVec1.subVectors(c, b);
        tempVec2.subVectors(a, b);
        // add the normal to the map for all vertices
        const normal = new __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$three$2f$build$2f$three$2e$core$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["Vector3"]().crossVectors(tempVec1, tempVec2).normalize();
        for(let n = 0; n < 3; n++){
            const vert = verts[n];
            const hash = hashVertex(vert);
            if (!(hash in vertexMap)) {
                vertexMap[hash] = [];
            }
            vertexMap[hash].push(normal);
        }
    }
    // average normals from all vertices that share a common location if they are within the
    // provided crease threshold
    const normalArray = new Float32Array(posAttr.count * 3);
    const normAttr = new __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$three$2f$build$2f$three$2e$core$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["BufferAttribute"](normalArray, 3, false);
    for(let i = 0, l = posAttr.count / 3; i < l; i++){
        // get the face normal for this vertex
        const i3 = 3 * i;
        const a = verts[0].fromBufferAttribute(posAttr, i3 + 0);
        const b = verts[1].fromBufferAttribute(posAttr, i3 + 1);
        const c = verts[2].fromBufferAttribute(posAttr, i3 + 2);
        tempVec1.subVectors(c, b);
        tempVec2.subVectors(a, b);
        tempNorm.crossVectors(tempVec1, tempVec2).normalize();
        // average all normals that meet the threshold and set the normal value
        for(let n = 0; n < 3; n++){
            const vert = verts[n];
            const hash = hashVertex(vert);
            const otherNormals = vertexMap[hash];
            tempNorm2.set(0, 0, 0);
            for(let k = 0, lk = otherNormals.length; k < lk; k++){
                const otherNorm = otherNormals[k];
                if (tempNorm.dot(otherNorm) > creaseDot) {
                    tempNorm2.add(otherNorm);
                }
            }
            tempNorm2.normalize();
            normAttr.setXYZ(i3 + n, tempNorm2.x, tempNorm2.y, tempNorm2.z);
        }
    }
    resultGeometry.setAttribute('normal', normAttr);
    return resultGeometry;
}
;
}),
"[project]/node_modules/three/examples/jsm/lines/LineSegmentsGeometry.js [app-client] (ecmascript)", ((__turbopack_context__) => {
"use strict";

__turbopack_context__.s([
    "LineSegmentsGeometry",
    ()=>LineSegmentsGeometry
]);
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$three$2f$build$2f$three$2e$core$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/node_modules/three/build/three.core.js [app-client] (ecmascript)");
;
const _box = new __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$three$2f$build$2f$three$2e$core$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["Box3"]();
const _vector = new __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$three$2f$build$2f$three$2e$core$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["Vector3"]();
/**
 * A series of vertex pairs, forming line segments.
 *
 * This is used in {@link LineSegments2} to describe the shape.
 *
 * @augments InstancedBufferGeometry
 * @three_import import { LineSegmentsGeometry } from 'three/addons/lines/LineSegmentsGeometry.js';
 */ class LineSegmentsGeometry extends __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$three$2f$build$2f$three$2e$core$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["InstancedBufferGeometry"] {
    /**
	 * Constructs a new line segments geometry.
	 */ constructor(){
        super();
        /**
		 * This flag can be used for type testing.
		 *
		 * @type {boolean}
		 * @readonly
		 * @default true
		 */ this.isLineSegmentsGeometry = true;
        this.type = 'LineSegmentsGeometry';
        const positions = [
            -1,
            2,
            0,
            1,
            2,
            0,
            -1,
            1,
            0,
            1,
            1,
            0,
            -1,
            0,
            0,
            1,
            0,
            0,
            -1,
            -1,
            0,
            1,
            -1,
            0
        ];
        const uvs = [
            -1,
            2,
            1,
            2,
            -1,
            1,
            1,
            1,
            -1,
            -1,
            1,
            -1,
            -1,
            -2,
            1,
            -2
        ];
        const index = [
            0,
            2,
            1,
            2,
            3,
            1,
            2,
            4,
            3,
            4,
            5,
            3,
            4,
            6,
            5,
            6,
            7,
            5
        ];
        this.setIndex(index);
        this.setAttribute('position', new __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$three$2f$build$2f$three$2e$core$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["Float32BufferAttribute"](positions, 3));
        this.setAttribute('uv', new __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$three$2f$build$2f$three$2e$core$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["Float32BufferAttribute"](uvs, 2));
    }
    /**
	 * Applies the given 4x4 transformation matrix to the geometry.
	 *
	 * @param {Matrix4} matrix - The matrix to apply.
	 * @return {LineSegmentsGeometry} A reference to this instance.
	 */ applyMatrix4(matrix) {
        const start = this.attributes.instanceStart;
        const end = this.attributes.instanceEnd;
        if (start !== undefined) {
            start.applyMatrix4(matrix);
            end.applyMatrix4(matrix);
            start.needsUpdate = true;
        }
        if (this.boundingBox !== null) {
            this.computeBoundingBox();
        }
        if (this.boundingSphere !== null) {
            this.computeBoundingSphere();
        }
        return this;
    }
    /**
	 * Sets the given line positions for this geometry. The length must be a multiple of six since
	 * each line segment is defined by a start end vertex in the pattern `(xyz xyz)`.
	 *
	 * @param {Float32Array|Array<number>} array - The position data to set.
	 * @return {LineSegmentsGeometry} A reference to this geometry.
	 */ setPositions(array) {
        let lineSegments;
        if (array instanceof Float32Array) {
            lineSegments = array;
        } else if (Array.isArray(array)) {
            lineSegments = new Float32Array(array);
        }
        const instanceBuffer = new __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$three$2f$build$2f$three$2e$core$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["InstancedInterleavedBuffer"](lineSegments, 6, 1); // xyz, xyz
        this.setAttribute('instanceStart', new __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$three$2f$build$2f$three$2e$core$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["InterleavedBufferAttribute"](instanceBuffer, 3, 0)); // xyz
        this.setAttribute('instanceEnd', new __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$three$2f$build$2f$three$2e$core$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["InterleavedBufferAttribute"](instanceBuffer, 3, 3)); // xyz
        this.instanceCount = this.attributes.instanceStart.count;
        //
        this.computeBoundingBox();
        this.computeBoundingSphere();
        return this;
    }
    /**
	 * Sets the given line colors for this geometry. The length must be a multiple of six since
	 * each line segment is defined by a start end color in the pattern `(rgb rgb)`.
	 *
	 * @param {Float32Array|Array<number>} array - The position data to set.
	 * @return {LineSegmentsGeometry} A reference to this geometry.
	 */ setColors(array) {
        let colors;
        if (array instanceof Float32Array) {
            colors = array;
        } else if (Array.isArray(array)) {
            colors = new Float32Array(array);
        }
        const instanceColorBuffer = new __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$three$2f$build$2f$three$2e$core$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["InstancedInterleavedBuffer"](colors, 6, 1); // rgb, rgb
        this.setAttribute('instanceColorStart', new __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$three$2f$build$2f$three$2e$core$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["InterleavedBufferAttribute"](instanceColorBuffer, 3, 0)); // rgb
        this.setAttribute('instanceColorEnd', new __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$three$2f$build$2f$three$2e$core$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["InterleavedBufferAttribute"](instanceColorBuffer, 3, 3)); // rgb
        return this;
    }
    /**
	 * Setups this line segments geometry from the given wireframe geometry.
	 *
	 * @param {WireframeGeometry} geometry - The geometry that should be used as a data source for this geometry.
	 * @return {LineSegmentsGeometry} A reference to this geometry.
	 */ fromWireframeGeometry(geometry) {
        this.setPositions(geometry.attributes.position.array);
        return this;
    }
    /**
	 * Setups this line segments geometry from the given edges geometry.
	 *
	 * @param {EdgesGeometry} geometry - The geometry that should be used as a data source for this geometry.
	 * @return {LineSegmentsGeometry} A reference to this geometry.
	 */ fromEdgesGeometry(geometry) {
        this.setPositions(geometry.attributes.position.array);
        return this;
    }
    /**
	 * Setups this line segments geometry from the given mesh.
	 *
	 * @param {Mesh} mesh - The mesh geometry that should be used as a data source for this geometry.
	 * @return {LineSegmentsGeometry} A reference to this geometry.
	 */ fromMesh(mesh) {
        this.fromWireframeGeometry(new __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$three$2f$build$2f$three$2e$core$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["WireframeGeometry"](mesh.geometry));
        // set colors, maybe
        return this;
    }
    /**
	 * Setups this line segments geometry from the given line segments.
	 *
	 * @param {LineSegments} lineSegments - The line segments that should be used as a data source for this geometry.
	 * Assumes the source geometry is not using indices.
	 * @return {LineSegmentsGeometry} A reference to this geometry.
	 */ fromLineSegments(lineSegments) {
        const geometry = lineSegments.geometry;
        this.setPositions(geometry.attributes.position.array); // assumes non-indexed
        // set colors, maybe
        return this;
    }
    computeBoundingBox() {
        if (this.boundingBox === null) {
            this.boundingBox = new __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$three$2f$build$2f$three$2e$core$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["Box3"]();
        }
        const start = this.attributes.instanceStart;
        const end = this.attributes.instanceEnd;
        if (start !== undefined && end !== undefined) {
            this.boundingBox.setFromBufferAttribute(start);
            _box.setFromBufferAttribute(end);
            this.boundingBox.union(_box);
        }
    }
    computeBoundingSphere() {
        if (this.boundingSphere === null) {
            this.boundingSphere = new __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$three$2f$build$2f$three$2e$core$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["Sphere"]();
        }
        if (this.boundingBox === null) {
            this.computeBoundingBox();
        }
        const start = this.attributes.instanceStart;
        const end = this.attributes.instanceEnd;
        if (start !== undefined && end !== undefined) {
            const center = this.boundingSphere.center;
            this.boundingBox.getCenter(center);
            let maxRadiusSq = 0;
            for(let i = 0, il = start.count; i < il; i++){
                _vector.fromBufferAttribute(start, i);
                maxRadiusSq = Math.max(maxRadiusSq, center.distanceToSquared(_vector));
                _vector.fromBufferAttribute(end, i);
                maxRadiusSq = Math.max(maxRadiusSq, center.distanceToSquared(_vector));
            }
            this.boundingSphere.radius = Math.sqrt(maxRadiusSq);
            if (isNaN(this.boundingSphere.radius)) {
                console.error('THREE.LineSegmentsGeometry.computeBoundingSphere(): Computed radius is NaN. The instanced position data is likely to have NaN values.', this);
            }
        }
    }
    toJSON() {
    // todo
    }
}
;
}),
"[project]/node_modules/three/examples/jsm/lines/LineMaterial.js [app-client] (ecmascript)", ((__turbopack_context__) => {
"use strict";

__turbopack_context__.s([
    "LineMaterial",
    ()=>LineMaterial
]);
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$three$2f$build$2f$three$2e$module$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__$3c$locals$3e$__ = __turbopack_context__.i("[project]/node_modules/three/build/three.module.js [app-client] (ecmascript) <locals>");
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$three$2f$build$2f$three$2e$core$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/node_modules/three/build/three.core.js [app-client] (ecmascript)");
;
__TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$three$2f$build$2f$three$2e$module$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__$3c$locals$3e$__["UniformsLib"].line = {
    worldUnits: {
        value: 1
    },
    linewidth: {
        value: 1
    },
    resolution: {
        value: new __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$three$2f$build$2f$three$2e$core$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["Vector2"](1, 1)
    },
    dashOffset: {
        value: 0
    },
    dashScale: {
        value: 1
    },
    dashSize: {
        value: 1
    },
    gapSize: {
        value: 1
    } // todo FIX - maybe change to totalSize
};
__TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$three$2f$build$2f$three$2e$module$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__$3c$locals$3e$__["ShaderLib"]['line'] = {
    uniforms: __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$three$2f$build$2f$three$2e$core$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["UniformsUtils"].merge([
        __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$three$2f$build$2f$three$2e$module$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__$3c$locals$3e$__["UniformsLib"].common,
        __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$three$2f$build$2f$three$2e$module$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__$3c$locals$3e$__["UniformsLib"].fog,
        __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$three$2f$build$2f$three$2e$module$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__$3c$locals$3e$__["UniformsLib"].line
    ]),
    vertexShader: /* glsl */ `
		#include <common>
		#include <color_pars_vertex>
		#include <fog_pars_vertex>
		#include <logdepthbuf_pars_vertex>
		#include <clipping_planes_pars_vertex>

		uniform float linewidth;
		uniform vec2 resolution;

		attribute vec3 instanceStart;
		attribute vec3 instanceEnd;

		attribute vec3 instanceColorStart;
		attribute vec3 instanceColorEnd;

		#ifdef WORLD_UNITS

			varying vec4 worldPos;
			varying vec3 worldStart;
			varying vec3 worldEnd;

			#ifdef USE_DASH

				varying vec2 vUv;

			#endif

		#else

			varying vec2 vUv;

		#endif

		#ifdef USE_DASH

			uniform float dashScale;
			attribute float instanceDistanceStart;
			attribute float instanceDistanceEnd;
			varying float vLineDistance;

		#endif

		void trimSegment( const in vec4 start, inout vec4 end ) {

			// trim end segment so it terminates between the camera plane and the near plane

			// conservative estimate of the near plane
			float a = projectionMatrix[ 2 ][ 2 ]; // 3nd entry in 3th column
			float b = projectionMatrix[ 3 ][ 2 ]; // 3nd entry in 4th column
			float nearEstimate = - 0.5 * b / a;

			float alpha = ( nearEstimate - start.z ) / ( end.z - start.z );

			end.xyz = mix( start.xyz, end.xyz, alpha );

		}

		void main() {

			#ifdef USE_COLOR

				vColor.xyz = ( position.y < 0.5 ) ? instanceColorStart : instanceColorEnd;

			#endif

			#ifdef USE_DASH

				vLineDistance = ( position.y < 0.5 ) ? dashScale * instanceDistanceStart : dashScale * instanceDistanceEnd;
				vUv = uv;

			#endif

			float aspect = resolution.x / resolution.y;

			// camera space
			vec4 start = modelViewMatrix * vec4( instanceStart, 1.0 );
			vec4 end = modelViewMatrix * vec4( instanceEnd, 1.0 );

			#ifdef WORLD_UNITS

				worldStart = start.xyz;
				worldEnd = end.xyz;

			#else

				vUv = uv;

			#endif

			// special case for perspective projection, and segments that terminate either in, or behind, the camera plane
			// clearly the gpu firmware has a way of addressing this issue when projecting into ndc space
			// but we need to perform ndc-space calculations in the shader, so we must address this issue directly
			// perhaps there is a more elegant solution -- WestLangley

			bool perspective = ( projectionMatrix[ 2 ][ 3 ] == - 1.0 ); // 4th entry in the 3rd column

			if ( perspective ) {

				if ( start.z < 0.0 && end.z >= 0.0 ) {

					trimSegment( start, end );

				} else if ( end.z < 0.0 && start.z >= 0.0 ) {

					trimSegment( end, start );

				}

			}

			// clip space
			vec4 clipStart = projectionMatrix * start;
			vec4 clipEnd = projectionMatrix * end;

			// ndc space
			vec3 ndcStart = clipStart.xyz / clipStart.w;
			vec3 ndcEnd = clipEnd.xyz / clipEnd.w;

			// direction
			vec2 dir = ndcEnd.xy - ndcStart.xy;

			// account for clip-space aspect ratio
			dir.x *= aspect;
			dir = normalize( dir );

			#ifdef WORLD_UNITS

				vec3 worldDir = normalize( end.xyz - start.xyz );
				vec3 tmpFwd = normalize( mix( start.xyz, end.xyz, 0.5 ) );
				vec3 worldUp = normalize( cross( worldDir, tmpFwd ) );
				vec3 worldFwd = cross( worldDir, worldUp );
				worldPos = position.y < 0.5 ? start: end;

				// height offset
				float hw = linewidth * 0.5;
				worldPos.xyz += position.x < 0.0 ? hw * worldUp : - hw * worldUp;

				// don't extend the line if we're rendering dashes because we
				// won't be rendering the endcaps
				#ifndef USE_DASH

					// cap extension
					worldPos.xyz += position.y < 0.5 ? - hw * worldDir : hw * worldDir;

					// add width to the box
					worldPos.xyz += worldFwd * hw;

					// endcaps
					if ( position.y > 1.0 || position.y < 0.0 ) {

						worldPos.xyz -= worldFwd * 2.0 * hw;

					}

				#endif

				// project the worldpos
				vec4 clip = projectionMatrix * worldPos;

				// shift the depth of the projected points so the line
				// segments overlap neatly
				vec3 clipPose = ( position.y < 0.5 ) ? ndcStart : ndcEnd;
				clip.z = clipPose.z * clip.w;

			#else

				vec2 offset = vec2( dir.y, - dir.x );
				// undo aspect ratio adjustment
				dir.x /= aspect;
				offset.x /= aspect;

				// sign flip
				if ( position.x < 0.0 ) offset *= - 1.0;

				// endcaps
				if ( position.y < 0.0 ) {

					offset += - dir;

				} else if ( position.y > 1.0 ) {

					offset += dir;

				}

				// adjust for linewidth
				offset *= linewidth;

				// adjust for clip-space to screen-space conversion // maybe resolution should be based on viewport ...
				offset /= resolution.y;

				// select end
				vec4 clip = ( position.y < 0.5 ) ? clipStart : clipEnd;

				// back to clip space
				offset *= clip.w;

				clip.xy += offset;

			#endif

			gl_Position = clip;

			vec4 mvPosition = ( position.y < 0.5 ) ? start : end; // this is an approximation

			#include <logdepthbuf_vertex>
			#include <clipping_planes_vertex>
			#include <fog_vertex>

		}
		`,
    fragmentShader: /* glsl */ `
		uniform vec3 diffuse;
		uniform float opacity;
		uniform float linewidth;

		#ifdef USE_DASH

			uniform float dashOffset;
			uniform float dashSize;
			uniform float gapSize;

		#endif

		varying float vLineDistance;

		#ifdef WORLD_UNITS

			varying vec4 worldPos;
			varying vec3 worldStart;
			varying vec3 worldEnd;

			#ifdef USE_DASH

				varying vec2 vUv;

			#endif

		#else

			varying vec2 vUv;

		#endif

		#include <common>
		#include <color_pars_fragment>
		#include <fog_pars_fragment>
		#include <logdepthbuf_pars_fragment>
		#include <clipping_planes_pars_fragment>

		vec2 closestLineToLine(vec3 p1, vec3 p2, vec3 p3, vec3 p4) {

			float mua;
			float mub;

			vec3 p13 = p1 - p3;
			vec3 p43 = p4 - p3;

			vec3 p21 = p2 - p1;

			float d1343 = dot( p13, p43 );
			float d4321 = dot( p43, p21 );
			float d1321 = dot( p13, p21 );
			float d4343 = dot( p43, p43 );
			float d2121 = dot( p21, p21 );

			float denom = d2121 * d4343 - d4321 * d4321;

			float numer = d1343 * d4321 - d1321 * d4343;

			mua = numer / denom;
			mua = clamp( mua, 0.0, 1.0 );
			mub = ( d1343 + d4321 * ( mua ) ) / d4343;
			mub = clamp( mub, 0.0, 1.0 );

			return vec2( mua, mub );

		}

		void main() {

			float alpha = opacity;
			vec4 diffuseColor = vec4( diffuse, alpha );

			#include <clipping_planes_fragment>

			#ifdef USE_DASH

				if ( vUv.y < - 1.0 || vUv.y > 1.0 ) discard; // discard endcaps

				if ( mod( vLineDistance + dashOffset, dashSize + gapSize ) > dashSize ) discard; // todo - FIX

			#endif

			#ifdef WORLD_UNITS

				// Find the closest points on the view ray and the line segment
				vec3 rayEnd = normalize( worldPos.xyz ) * 1e5;
				vec3 lineDir = worldEnd - worldStart;
				vec2 params = closestLineToLine( worldStart, worldEnd, vec3( 0.0, 0.0, 0.0 ), rayEnd );

				vec3 p1 = worldStart + lineDir * params.x;
				vec3 p2 = rayEnd * params.y;
				vec3 delta = p1 - p2;
				float len = length( delta );
				float norm = len / linewidth;

				#ifndef USE_DASH

					#ifdef USE_ALPHA_TO_COVERAGE

						float dnorm = fwidth( norm );
						alpha = 1.0 - smoothstep( 0.5 - dnorm, 0.5 + dnorm, norm );

					#else

						if ( norm > 0.5 ) {

							discard;

						}

					#endif

				#endif

			#else

				#ifdef USE_ALPHA_TO_COVERAGE

					// artifacts appear on some hardware if a derivative is taken within a conditional
					float a = vUv.x;
					float b = ( vUv.y > 0.0 ) ? vUv.y - 1.0 : vUv.y + 1.0;
					float len2 = a * a + b * b;
					float dlen = fwidth( len2 );

					if ( abs( vUv.y ) > 1.0 ) {

						alpha = 1.0 - smoothstep( 1.0 - dlen, 1.0 + dlen, len2 );

					}

				#else

					if ( abs( vUv.y ) > 1.0 ) {

						float a = vUv.x;
						float b = ( vUv.y > 0.0 ) ? vUv.y - 1.0 : vUv.y + 1.0;
						float len2 = a * a + b * b;

						if ( len2 > 1.0 ) discard;

					}

				#endif

			#endif

			#include <logdepthbuf_fragment>
			#include <color_fragment>

			gl_FragColor = vec4( diffuseColor.rgb, alpha );

			#include <tonemapping_fragment>
			#include <colorspace_fragment>
			#include <fog_fragment>
			#include <premultiplied_alpha_fragment>

		}
		`
};
/**
 * A material for drawing wireframe-style geometries.
 *
 * Unlike {@link LineBasicMaterial}, it supports arbitrary line widths and allows using world units
 * instead of screen space units. This material is used with {@link LineSegments2} and {@link Line2}.
 *
 * This module can only be used with {@link WebGLRenderer}. When using {@link WebGPURenderer},
 * use {@link Line2NodeMaterial}.
 *
 * @augments ShaderMaterial
 * @three_import import { LineMaterial } from 'three/addons/lines/LineMaterial.js';
 */ class LineMaterial extends __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$three$2f$build$2f$three$2e$core$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["ShaderMaterial"] {
    /**
	 * Constructs a new line segments geometry.
	 *
	 * @param {Object} [parameters] - An object with one or more properties
	 * defining the material's appearance. Any property of the material
	 * (including any property from inherited materials) can be passed
	 * in here. Color values can be passed any type of value accepted
	 * by {@link Color#set}.
	 */ constructor(parameters){
        super({
            type: 'LineMaterial',
            uniforms: __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$three$2f$build$2f$three$2e$core$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["UniformsUtils"].clone(__TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$three$2f$build$2f$three$2e$module$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__$3c$locals$3e$__["ShaderLib"]['line'].uniforms),
            vertexShader: __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$three$2f$build$2f$three$2e$module$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__$3c$locals$3e$__["ShaderLib"]['line'].vertexShader,
            fragmentShader: __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$three$2f$build$2f$three$2e$module$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__$3c$locals$3e$__["ShaderLib"]['line'].fragmentShader,
            clipping: true // required for clipping support
        });
        /**
		 * This flag can be used for type testing.
		 *
		 * @type {boolean}
		 * @readonly
		 * @default true
		 */ this.isLineMaterial = true;
        this.setValues(parameters);
    }
    /**
	 * The material's color.
	 *
	 * @type {Color}
	 * @default (1,1,1)
	 */ get color() {
        return this.uniforms.diffuse.value;
    }
    set color(value) {
        this.uniforms.diffuse.value = value;
    }
    /**
	 * Whether the material's sizes (width, dash gaps) are in world units.
	 *
	 * @type {boolean}
	 * @default false
	 */ get worldUnits() {
        return 'WORLD_UNITS' in this.defines;
    }
    set worldUnits(value) {
        if (value === true) {
            this.defines.WORLD_UNITS = '';
        } else {
            delete this.defines.WORLD_UNITS;
        }
    }
    /**
	 * Controls line thickness in CSS pixel units when `worldUnits` is `false` (default),
	 * or in world units when `worldUnits` is `true`.
	 *
	 * @type {number}
	 * @default 1
	 */ get linewidth() {
        return this.uniforms.linewidth.value;
    }
    set linewidth(value) {
        if (!this.uniforms.linewidth) return;
        this.uniforms.linewidth.value = value;
    }
    /**
	 * Whether the line is dashed, or solid.
	 *
	 * @type {boolean}
	 * @default false
	 */ get dashed() {
        return 'USE_DASH' in this.defines;
    }
    set dashed(value) {
        if (value === true !== this.dashed) {
            this.needsUpdate = true;
        }
        if (value === true) {
            this.defines.USE_DASH = '';
        } else {
            delete this.defines.USE_DASH;
        }
    }
    /**
	 * The scale of the dashes and gaps.
	 *
	 * @type {number}
	 * @default 1
	 */ get dashScale() {
        return this.uniforms.dashScale.value;
    }
    set dashScale(value) {
        this.uniforms.dashScale.value = value;
    }
    /**
	 * The size of the dash.
	 *
	 * @type {number}
	 * @default 1
	 */ get dashSize() {
        return this.uniforms.dashSize.value;
    }
    set dashSize(value) {
        this.uniforms.dashSize.value = value;
    }
    /**
	 * Where in the dash cycle the dash starts.
	 *
	 * @type {number}
	 * @default 0
	 */ get dashOffset() {
        return this.uniforms.dashOffset.value;
    }
    set dashOffset(value) {
        this.uniforms.dashOffset.value = value;
    }
    /**
	 * The size of the gap.
	 *
	 * @type {number}
	 * @default 0
	 */ get gapSize() {
        return this.uniforms.gapSize.value;
    }
    set gapSize(value) {
        this.uniforms.gapSize.value = value;
    }
    /**
	 * The opacity.
	 *
	 * @type {number}
	 * @default 1
	 */ get opacity() {
        return this.uniforms.opacity.value;
    }
    set opacity(value) {
        if (!this.uniforms) return;
        this.uniforms.opacity.value = value;
    }
    /**
	 * The size of the viewport, in screen pixels. This must be kept updated to make
	 * screen-space rendering accurate.The `LineSegments2.onBeforeRender` callback
	 * performs the update for visible objects.
	 *
	 * @type {Vector2}
	 */ get resolution() {
        return this.uniforms.resolution.value;
    }
    set resolution(value) {
        this.uniforms.resolution.value.copy(value);
    }
    /**
	 * Whether to use alphaToCoverage or not. When enabled, this can improve the
	 * anti-aliasing of line edges when using MSAA.
	 *
	 * @type {boolean}
	 */ get alphaToCoverage() {
        return 'USE_ALPHA_TO_COVERAGE' in this.defines;
    }
    set alphaToCoverage(value) {
        if (!this.defines) return;
        if (value === true !== this.alphaToCoverage) {
            this.needsUpdate = true;
        }
        if (value === true) {
            this.defines.USE_ALPHA_TO_COVERAGE = '';
        } else {
            delete this.defines.USE_ALPHA_TO_COVERAGE;
        }
    }
}
;
}),
"[project]/node_modules/three/examples/jsm/lines/LineSegments2.js [app-client] (ecmascript)", ((__turbopack_context__) => {
"use strict";

__turbopack_context__.s([
    "LineSegments2",
    ()=>LineSegments2
]);
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$three$2f$build$2f$three$2e$core$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/node_modules/three/build/three.core.js [app-client] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$three$2f$examples$2f$jsm$2f$lines$2f$LineSegmentsGeometry$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/node_modules/three/examples/jsm/lines/LineSegmentsGeometry.js [app-client] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$three$2f$examples$2f$jsm$2f$lines$2f$LineMaterial$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/node_modules/three/examples/jsm/lines/LineMaterial.js [app-client] (ecmascript)");
;
;
;
const _viewport = new __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$three$2f$build$2f$three$2e$core$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["Vector4"]();
const _start = new __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$three$2f$build$2f$three$2e$core$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["Vector3"]();
const _end = new __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$three$2f$build$2f$three$2e$core$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["Vector3"]();
const _start4 = new __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$three$2f$build$2f$three$2e$core$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["Vector4"]();
const _end4 = new __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$three$2f$build$2f$three$2e$core$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["Vector4"]();
const _ssOrigin = new __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$three$2f$build$2f$three$2e$core$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["Vector4"]();
const _ssOrigin3 = new __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$three$2f$build$2f$three$2e$core$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["Vector3"]();
const _mvMatrix = new __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$three$2f$build$2f$three$2e$core$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["Matrix4"]();
const _line = new __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$three$2f$build$2f$three$2e$core$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["Line3"]();
const _closestPoint = new __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$three$2f$build$2f$three$2e$core$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["Vector3"]();
const _box = new __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$three$2f$build$2f$three$2e$core$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["Box3"]();
const _sphere = new __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$three$2f$build$2f$three$2e$core$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["Sphere"]();
const _clipToWorldVector = new __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$three$2f$build$2f$three$2e$core$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["Vector4"]();
let _ray, _lineWidth;
// Returns the margin required to expand by in world space given the distance from the camera,
// line width, resolution, and camera projection
function getWorldSpaceHalfWidth(camera, distance, resolution) {
    // transform into clip space, adjust the x and y values by the pixel width offset, then
    // transform back into world space to get world offset. Note clip space is [-1, 1] so full
    // width does not need to be halved.
    _clipToWorldVector.set(0, 0, -distance, 1.0).applyMatrix4(camera.projectionMatrix);
    _clipToWorldVector.multiplyScalar(1.0 / _clipToWorldVector.w);
    _clipToWorldVector.x = _lineWidth / resolution.width;
    _clipToWorldVector.y = _lineWidth / resolution.height;
    _clipToWorldVector.applyMatrix4(camera.projectionMatrixInverse);
    _clipToWorldVector.multiplyScalar(1.0 / _clipToWorldVector.w);
    return Math.abs(Math.max(_clipToWorldVector.x, _clipToWorldVector.y));
}
function raycastWorldUnits(lineSegments, intersects) {
    const matrixWorld = lineSegments.matrixWorld;
    const geometry = lineSegments.geometry;
    const instanceStart = geometry.attributes.instanceStart;
    const instanceEnd = geometry.attributes.instanceEnd;
    const segmentCount = Math.min(geometry.instanceCount, instanceStart.count);
    for(let i = 0, l = segmentCount; i < l; i++){
        _line.start.fromBufferAttribute(instanceStart, i);
        _line.end.fromBufferAttribute(instanceEnd, i);
        _line.applyMatrix4(matrixWorld);
        const pointOnLine = new __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$three$2f$build$2f$three$2e$core$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["Vector3"]();
        const point = new __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$three$2f$build$2f$three$2e$core$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["Vector3"]();
        _ray.distanceSqToSegment(_line.start, _line.end, point, pointOnLine);
        const isInside = point.distanceTo(pointOnLine) < _lineWidth * 0.5;
        if (isInside) {
            intersects.push({
                point,
                pointOnLine,
                distance: _ray.origin.distanceTo(point),
                object: lineSegments,
                face: null,
                faceIndex: i,
                uv: null,
                uv1: null
            });
        }
    }
}
function raycastScreenSpace(lineSegments, camera, intersects) {
    const projectionMatrix = camera.projectionMatrix;
    const material = lineSegments.material;
    const resolution = material.resolution;
    const matrixWorld = lineSegments.matrixWorld;
    const geometry = lineSegments.geometry;
    const instanceStart = geometry.attributes.instanceStart;
    const instanceEnd = geometry.attributes.instanceEnd;
    const segmentCount = Math.min(geometry.instanceCount, instanceStart.count);
    const near = -camera.near;
    //
    // pick a point 1 unit out along the ray to avoid the ray origin
    // sitting at the camera origin which will cause "w" to be 0 when
    // applying the projection matrix.
    _ray.at(1, _ssOrigin);
    // ndc space [ - 1.0, 1.0 ]
    _ssOrigin.w = 1;
    _ssOrigin.applyMatrix4(camera.matrixWorldInverse);
    _ssOrigin.applyMatrix4(projectionMatrix);
    _ssOrigin.multiplyScalar(1 / _ssOrigin.w);
    // screen space
    _ssOrigin.x *= resolution.x / 2;
    _ssOrigin.y *= resolution.y / 2;
    _ssOrigin.z = 0;
    _ssOrigin3.copy(_ssOrigin);
    _mvMatrix.multiplyMatrices(camera.matrixWorldInverse, matrixWorld);
    for(let i = 0, l = segmentCount; i < l; i++){
        _start4.fromBufferAttribute(instanceStart, i);
        _end4.fromBufferAttribute(instanceEnd, i);
        _start4.w = 1;
        _end4.w = 1;
        // camera space
        _start4.applyMatrix4(_mvMatrix);
        _end4.applyMatrix4(_mvMatrix);
        // skip the segment if it's entirely behind the camera
        const isBehindCameraNear = _start4.z > near && _end4.z > near;
        if (isBehindCameraNear) {
            continue;
        }
        // trim the segment if it extends behind camera near
        if (_start4.z > near) {
            const deltaDist = _start4.z - _end4.z;
            const t = (_start4.z - near) / deltaDist;
            _start4.lerp(_end4, t);
        } else if (_end4.z > near) {
            const deltaDist = _end4.z - _start4.z;
            const t = (_end4.z - near) / deltaDist;
            _end4.lerp(_start4, t);
        }
        // clip space
        _start4.applyMatrix4(projectionMatrix);
        _end4.applyMatrix4(projectionMatrix);
        // ndc space [ - 1.0, 1.0 ]
        _start4.multiplyScalar(1 / _start4.w);
        _end4.multiplyScalar(1 / _end4.w);
        // screen space
        _start4.x *= resolution.x / 2;
        _start4.y *= resolution.y / 2;
        _end4.x *= resolution.x / 2;
        _end4.y *= resolution.y / 2;
        // create 2d segment
        _line.start.copy(_start4);
        _line.start.z = 0;
        _line.end.copy(_end4);
        _line.end.z = 0;
        // get closest point on ray to segment
        const param = _line.closestPointToPointParameter(_ssOrigin3, true);
        _line.at(param, _closestPoint);
        // check if the intersection point is within clip space
        const zPos = __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$three$2f$build$2f$three$2e$core$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["MathUtils"].lerp(_start4.z, _end4.z, param);
        const isInClipSpace = zPos >= -1 && zPos <= 1;
        const isInside = _ssOrigin3.distanceTo(_closestPoint) < _lineWidth * 0.5;
        if (isInClipSpace && isInside) {
            _line.start.fromBufferAttribute(instanceStart, i);
            _line.end.fromBufferAttribute(instanceEnd, i);
            _line.start.applyMatrix4(matrixWorld);
            _line.end.applyMatrix4(matrixWorld);
            const pointOnLine = new __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$three$2f$build$2f$three$2e$core$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["Vector3"]();
            const point = new __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$three$2f$build$2f$three$2e$core$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["Vector3"]();
            _ray.distanceSqToSegment(_line.start, _line.end, point, pointOnLine);
            intersects.push({
                point: point,
                pointOnLine: pointOnLine,
                distance: _ray.origin.distanceTo(point),
                object: lineSegments,
                face: null,
                faceIndex: i,
                uv: null,
                uv1: null
            });
        }
    }
}
/**
 * A series of lines drawn between pairs of vertices.
 *
 * This adds functionality beyond {@link LineSegments}, like arbitrary line width and changing width
 * to be in world units. {@link Line2} extends this object, forming a polyline instead of individual
 * segments.
 *
 * This module can only be used with {@link WebGLRenderer}. When using {@link WebGPURenderer},
 * import the class from `lines/webgpu/LineSegments2.js`.
 *
 *  ```js
 * const geometry = new LineSegmentsGeometry();
 * geometry.setPositions( positions );
 * geometry.setColors( colors );
 *
 * const material = new LineMaterial( { linewidth: 5, vertexColors: true } };
 *
 * const lineSegments = new LineSegments2( geometry, material );
 * scene.add( lineSegments );
 * ```
 *
 * @augments Mesh
 * @three_import import { LineSegments2 } from 'three/addons/lines/LineSegments2.js';
 */ class LineSegments2 extends __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$three$2f$build$2f$three$2e$core$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["Mesh"] {
    /**
	 * Constructs a new wide line.
	 *
	 * @param {LineSegmentsGeometry} [geometry] - The line geometry.
	 * @param {LineMaterial} [material] - The line material.
	 */ constructor(geometry = new __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$three$2f$examples$2f$jsm$2f$lines$2f$LineSegmentsGeometry$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["LineSegmentsGeometry"](), material = new __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$three$2f$examples$2f$jsm$2f$lines$2f$LineMaterial$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["LineMaterial"]({
        color: Math.random() * 0xffffff
    })){
        super(geometry, material);
        /**
		 * This flag can be used for type testing.
		 *
		 * @type {boolean}
		 * @readonly
		 * @default true
		 */ this.isLineSegments2 = true;
        this.type = 'LineSegments2';
    }
    /**
	 * Computes an array of distance values which are necessary for rendering dashed lines.
	 * For each vertex in the geometry, the method calculates the cumulative length from the
	 * current point to the very beginning of the line.
	 *
	 * @return {LineSegments2} A reference to this instance.
	 */ computeLineDistances() {
        // for backwards-compatibility, but could be a method of LineSegmentsGeometry...
        const geometry = this.geometry;
        const instanceStart = geometry.attributes.instanceStart;
        const instanceEnd = geometry.attributes.instanceEnd;
        const lineDistances = new Float32Array(2 * instanceStart.count);
        for(let i = 0, j = 0, l = instanceStart.count; i < l; i++, j += 2){
            _start.fromBufferAttribute(instanceStart, i);
            _end.fromBufferAttribute(instanceEnd, i);
            lineDistances[j] = j === 0 ? 0 : lineDistances[j - 1];
            lineDistances[j + 1] = lineDistances[j] + _start.distanceTo(_end);
        }
        const instanceDistanceBuffer = new __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$three$2f$build$2f$three$2e$core$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["InstancedInterleavedBuffer"](lineDistances, 2, 1); // d0, d1
        geometry.setAttribute('instanceDistanceStart', new __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$three$2f$build$2f$three$2e$core$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["InterleavedBufferAttribute"](instanceDistanceBuffer, 1, 0)); // d0
        geometry.setAttribute('instanceDistanceEnd', new __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$three$2f$build$2f$three$2e$core$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["InterleavedBufferAttribute"](instanceDistanceBuffer, 1, 1)); // d1
        return this;
    }
    /**
	 * Computes intersection points between a casted ray and this instance.
	 *
	 * @param {Raycaster} raycaster - The raycaster.
	 * @param {Array<Object>} intersects - The target array that holds the intersection points.
	 */ raycast(raycaster, intersects) {
        const worldUnits = this.material.worldUnits;
        const camera = raycaster.camera;
        if (camera === null && !worldUnits) {
            console.error('LineSegments2: "Raycaster.camera" needs to be set in order to raycast against LineSegments2 while worldUnits is set to false.');
        }
        const threshold = raycaster.params.Line2 !== undefined ? raycaster.params.Line2.threshold || 0 : 0;
        _ray = raycaster.ray;
        const matrixWorld = this.matrixWorld;
        const geometry = this.geometry;
        const material = this.material;
        _lineWidth = material.linewidth + threshold;
        // check if we intersect the sphere bounds
        if (geometry.boundingSphere === null) {
            geometry.computeBoundingSphere();
        }
        _sphere.copy(geometry.boundingSphere).applyMatrix4(matrixWorld);
        // increase the sphere bounds by the worst case line screen space width
        let sphereMargin;
        if (worldUnits) {
            sphereMargin = _lineWidth * 0.5;
        } else {
            const distanceToSphere = Math.max(camera.near, _sphere.distanceToPoint(_ray.origin));
            sphereMargin = getWorldSpaceHalfWidth(camera, distanceToSphere, material.resolution);
        }
        _sphere.radius += sphereMargin;
        if (_ray.intersectsSphere(_sphere) === false) {
            return;
        }
        // check if we intersect the box bounds
        if (geometry.boundingBox === null) {
            geometry.computeBoundingBox();
        }
        _box.copy(geometry.boundingBox).applyMatrix4(matrixWorld);
        // increase the box bounds by the worst case line width
        let boxMargin;
        if (worldUnits) {
            boxMargin = _lineWidth * 0.5;
        } else {
            const distanceToBox = Math.max(camera.near, _box.distanceToPoint(_ray.origin));
            boxMargin = getWorldSpaceHalfWidth(camera, distanceToBox, material.resolution);
        }
        _box.expandByScalar(boxMargin);
        if (_ray.intersectsBox(_box) === false) {
            return;
        }
        if (worldUnits) {
            raycastWorldUnits(this, intersects);
        } else {
            raycastScreenSpace(this, camera, intersects);
        }
    }
    onBeforeRender(renderer) {
        const uniforms = this.material.uniforms;
        if (uniforms && uniforms.resolution) {
            renderer.getViewport(_viewport);
            this.material.uniforms.resolution.value.set(_viewport.z, _viewport.w);
        }
    }
}
;
}),
"[project]/node_modules/three/examples/jsm/lines/LineGeometry.js [app-client] (ecmascript)", ((__turbopack_context__) => {
"use strict";

__turbopack_context__.s([
    "LineGeometry",
    ()=>LineGeometry
]);
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$three$2f$examples$2f$jsm$2f$lines$2f$LineSegmentsGeometry$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/node_modules/three/examples/jsm/lines/LineSegmentsGeometry.js [app-client] (ecmascript)");
;
/**
 * A chain of vertices, forming a polyline.
 *
 * This is used in {@link Line2} to describe the shape.
 *
 * ```js
 * const points = [
 * 	new THREE.Vector3( - 10, 0, 0 ),
 * 	new THREE.Vector3( 0, 5, 0 ),
 * 	new THREE.Vector3( 10, 0, 0 ),
 * ];
 *
 * const geometry = new LineGeometry();
 * geometry.setFromPoints( points );
 * ```
 *
 * @augments LineSegmentsGeometry
 * @three_import import { LineLineGeometry2 } from 'three/addons/lines/LineGeometry.js';
 */ class LineGeometry extends __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$three$2f$examples$2f$jsm$2f$lines$2f$LineSegmentsGeometry$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["LineSegmentsGeometry"] {
    /**
	 * Constructs a new line geometry.
	 */ constructor(){
        super();
        /**
		 * This flag can be used for type testing.
		 *
		 * @type {boolean}
		 * @readonly
		 * @default true
		 */ this.isLineGeometry = true;
        this.type = 'LineGeometry';
    }
    /**
	 * Sets the given line positions for this geometry.
	 *
	 * @param {Float32Array|Array<number>} array - The position data to set.
	 * @return {LineGeometry} A reference to this geometry.
	 */ setPositions(array) {
        // converts [ x1, y1, z1,  x2, y2, z2, ... ] to pairs format
        const length = array.length - 3;
        const points = new Float32Array(2 * length);
        for(let i = 0; i < length; i += 3){
            points[2 * i] = array[i];
            points[2 * i + 1] = array[i + 1];
            points[2 * i + 2] = array[i + 2];
            points[2 * i + 3] = array[i + 3];
            points[2 * i + 4] = array[i + 4];
            points[2 * i + 5] = array[i + 5];
        }
        super.setPositions(points);
        return this;
    }
    /**
	 * Sets the given line colors for this geometry.
	 *
	 * @param {Float32Array|Array<number>} array - The position data to set.
	 * @return {LineGeometry} A reference to this geometry.
	 */ setColors(array) {
        // converts [ r1, g1, b1,  r2, g2, b2, ... ] to pairs format
        const length = array.length - 3;
        const colors = new Float32Array(2 * length);
        for(let i = 0; i < length; i += 3){
            colors[2 * i] = array[i];
            colors[2 * i + 1] = array[i + 1];
            colors[2 * i + 2] = array[i + 2];
            colors[2 * i + 3] = array[i + 3];
            colors[2 * i + 4] = array[i + 4];
            colors[2 * i + 5] = array[i + 5];
        }
        super.setColors(colors);
        return this;
    }
    /**
	 * Setups this line segments geometry from the given sequence of points.
	 *
	 * @param {Array<Vector3|Vector2>} points - An array of points in 2D or 3D space.
	 * @return {LineGeometry} A reference to this geometry.
	 */ setFromPoints(points) {
        // converts a vector3 or vector2 array to pairs format
        const length = points.length - 1;
        const positions = new Float32Array(6 * length);
        for(let i = 0; i < length; i++){
            positions[6 * i] = points[i].x;
            positions[6 * i + 1] = points[i].y;
            positions[6 * i + 2] = points[i].z || 0;
            positions[6 * i + 3] = points[i + 1].x;
            positions[6 * i + 4] = points[i + 1].y;
            positions[6 * i + 5] = points[i + 1].z || 0;
        }
        super.setPositions(positions);
        return this;
    }
    /**
	 * Setups this line segments geometry from the given line.
	 *
	 * @param {Line} line - The line that should be used as a data source for this geometry.
	 * @return {LineGeometry} A reference to this geometry.
	 */ fromLine(line) {
        const geometry = line.geometry;
        this.setPositions(geometry.attributes.position.array); // assumes non-indexed
        // set colors, maybe
        return this;
    }
}
;
}),
"[project]/node_modules/three/examples/jsm/lines/Line2.js [app-client] (ecmascript)", ((__turbopack_context__) => {
"use strict";

__turbopack_context__.s([
    "Line2",
    ()=>Line2
]);
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$three$2f$examples$2f$jsm$2f$lines$2f$LineSegments2$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/node_modules/three/examples/jsm/lines/LineSegments2.js [app-client] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$three$2f$examples$2f$jsm$2f$lines$2f$LineGeometry$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/node_modules/three/examples/jsm/lines/LineGeometry.js [app-client] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$three$2f$examples$2f$jsm$2f$lines$2f$LineMaterial$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/node_modules/three/examples/jsm/lines/LineMaterial.js [app-client] (ecmascript)");
;
;
;
/**
 * A polyline drawn between vertices.
 *
 * This adds functionality beyond {@link Line}, like arbitrary line width and changing width to
 * be in world units.It extends {@link LineSegments2}, simplifying constructing segments from a
 * chain of points.
 *
 * This module can only be used with {@link WebGLRenderer}. When using {@link WebGPURenderer},
 * import the class from `lines/webgpu/Line2.js`.
 *
 * ```js
 * const geometry = new LineGeometry();
 * geometry.setPositions( positions );
 * geometry.setColors( colors );
 *
 * const material = new LineMaterial( { linewidth: 5, vertexColors: true } };
 *
 * const line = new Line2( geometry, material );
 * scene.add( line );
 * ```
 *
 * @augments LineSegments2
 * @three_import import { Line2 } from 'three/addons/lines/Line2.js';
 */ class Line2 extends __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$three$2f$examples$2f$jsm$2f$lines$2f$LineSegments2$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["LineSegments2"] {
    /**
	 * Constructs a new wide line.
	 *
	 * @param {LineGeometry} [geometry] - The line geometry.
	 * @param {LineMaterial} [material] - The line material.
	 */ constructor(geometry = new __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$three$2f$examples$2f$jsm$2f$lines$2f$LineGeometry$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["LineGeometry"](), material = new __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$three$2f$examples$2f$jsm$2f$lines$2f$LineMaterial$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["LineMaterial"]({
        color: Math.random() * 0xffffff
    })){
        super(geometry, material);
        /**
		 * This flag can be used for type testing.
		 *
		 * @type {boolean}
		 * @readonly
		 * @default true
		 */ this.isLine2 = true;
        this.type = 'Line2';
    }
}
;
}),
"[project]/node_modules/three/examples/jsm/geometries/TextGeometry.js [app-client] (ecmascript)", ((__turbopack_context__) => {
"use strict";

__turbopack_context__.s([
    "TextGeometry",
    ()=>TextGeometry
]);
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$three$2f$build$2f$three$2e$core$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/node_modules/three/build/three.core.js [app-client] (ecmascript)");
;
/**
 * A class for generating text as a single geometry. It is constructed by providing a string of text, and a set of
 * parameters consisting of a loaded font and extrude settings.
 *
 * See the {@link FontLoader} page for additional details.
 *
 * `TextGeometry` uses [typeface.json](http://gero3.github.io/facetype.js/) generated fonts.
 * Some existing fonts can be found located in `/examples/fonts`.
 *
 * ```js
 * const loader = new FontLoader();
 * const font = await loader.loadAsync( 'fonts/helvetiker_regular.typeface.json' );
 * const geometry = new TextGeometry( 'Hello three.js!', {
 * 	font: font,
 * 	size: 80,
 * 	depth: 5,
 * 	curveSegments: 12
 * } );
 * ```
 *
 * @augments ExtrudeGeometry
 * @three_import import { TextGeometry } from 'three/addons/geometries/TextGeometry.js';
 */ class TextGeometry extends __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$three$2f$build$2f$three$2e$core$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["ExtrudeGeometry"] {
    /**
	 * Constructs a new text geometry.
	 *
	 * @param {string} text - The text that should be transformed into a geometry.
	 * @param {TextGeometry~Options} [parameters] - The text settings.
	 */ constructor(text, parameters = {}){
        const font = parameters.font;
        if (font === undefined) {
            super(); // generate default extrude geometry
        } else {
            const shapes = font.generateShapes(text, parameters.size, parameters.direction);
            // defaults
            if (parameters.depth === undefined) parameters.depth = 50;
            if (parameters.bevelThickness === undefined) parameters.bevelThickness = 10;
            if (parameters.bevelSize === undefined) parameters.bevelSize = 8;
            if (parameters.bevelEnabled === undefined) parameters.bevelEnabled = false;
            super(shapes, parameters);
        }
        this.type = 'TextGeometry';
    }
}
;
}),
"[project]/node_modules/three/examples/jsm/loaders/FontLoader.js [app-client] (ecmascript)", ((__turbopack_context__) => {
"use strict";

__turbopack_context__.s([
    "Font",
    ()=>Font,
    "FontLoader",
    ()=>FontLoader
]);
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$three$2f$build$2f$three$2e$core$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/node_modules/three/build/three.core.js [app-client] (ecmascript)");
;
/**
 * A loader for loading fonts.
 *
 * You can convert fonts online using [facetype.js](https://gero3.github.io/facetype.js/).
 *
 * ```js
 * const loader = new FontLoader();
 * const font = await loader.loadAsync( 'fonts/helvetiker_regular.typeface.json' );
 * ```
 *
 * @augments Loader
 * @three_import import { FontLoader } from 'three/addons/loaders/FontLoader.js';
 */ class FontLoader extends __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$three$2f$build$2f$three$2e$core$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["Loader"] {
    /**
	 * Constructs a new font loader.
	 *
	 * @param {LoadingManager} [manager] - The loading manager.
	 */ constructor(manager){
        super(manager);
    }
    /**
	 * Starts loading from the given URL and passes the loaded font
	 * to the `onLoad()` callback.
	 *
	 * @param {string} url - The path/URL of the file to be loaded. This can also be a data URI.
	 * @param {function(Font)} onLoad - Executed when the loading process has been finished.
	 * @param {onProgressCallback} onProgress - Executed while the loading is in progress.
	 * @param {onErrorCallback} onError - Executed when errors occur.
	 */ load(url, onLoad, onProgress, onError) {
        const scope = this;
        const loader = new __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$three$2f$build$2f$three$2e$core$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["FileLoader"](this.manager);
        loader.setPath(this.path);
        loader.setRequestHeader(this.requestHeader);
        loader.setWithCredentials(this.withCredentials);
        loader.load(url, function(text) {
            const font = scope.parse(JSON.parse(text));
            if (onLoad) onLoad(font);
        }, onProgress, onError);
    }
    /**
	 * Parses the given font data and returns the resulting font.
	 *
	 * @param {Object} json - The raw font data as a JSON object.
	 * @return {Font} The font.
	 */ parse(json) {
        return new Font(json);
    }
}
/**
 * Class representing a font.
 */ class Font {
    /**
	 * Constructs a new font.
	 *
	 * @param {Object} data - The font data as JSON.
	 */ constructor(data){
        /**
		 * This flag can be used for type testing.
		 *
		 * @type {boolean}
		 * @readonly
		 * @default true
		 */ this.isFont = true;
        this.type = 'Font';
        /**
		 * The font data as JSON.
		 *
		 * @type {Object}
		 */ this.data = data;
    }
    /**
	 * Generates geometry shapes from the given text and size. The result of this method
	 * should be used with {@link ShapeGeometry} to generate the actual geometry data.
	 *
	 * @param {string} text - The text.
	 * @param {number} [size=100] - The text size.
	 * @param {string} [direction='ltr'] - Char direction: ltr(left to right), rtl(right to left) & tb(top bottom).
	 * @return {Array<Shape>} An array of shapes representing the text.
	 */ generateShapes(text, size = 100, direction = 'ltr') {
        const shapes = [];
        const paths = createPaths(text, size, this.data, direction);
        for(let p = 0, pl = paths.length; p < pl; p++){
            shapes.push(...paths[p].toShapes());
        }
        return shapes;
    }
}
function createPaths(text, size, data, direction) {
    const chars = Array.from(text);
    const scale = size / data.resolution;
    const line_height = (data.boundingBox.yMax - data.boundingBox.yMin + data.underlineThickness) * scale;
    const paths = [];
    let offsetX = 0, offsetY = 0;
    if (direction == 'rtl' || direction == 'tb') {
        chars.reverse();
    }
    for(let i = 0; i < chars.length; i++){
        const char = chars[i];
        if (char === '\n') {
            offsetX = 0;
            offsetY -= line_height;
        } else {
            const ret = createPath(char, scale, offsetX, offsetY, data);
            if (direction == 'tb') {
                offsetX = 0;
                offsetY += data.ascender * scale;
            } else {
                offsetX += ret.offsetX;
            }
            paths.push(ret.path);
        }
    }
    return paths;
}
function createPath(char, scale, offsetX, offsetY, data) {
    const glyph = data.glyphs[char] || data.glyphs['?'];
    if (!glyph) {
        console.error('THREE.Font: character "' + char + '" does not exists in font family ' + data.familyName + '.');
        return;
    }
    const path = new __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$three$2f$build$2f$three$2e$core$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["ShapePath"]();
    let x, y, cpx, cpy, cpx1, cpy1, cpx2, cpy2;
    if (glyph.o) {
        const outline = glyph._cachedOutline || (glyph._cachedOutline = glyph.o.split(' '));
        for(let i = 0, l = outline.length; i < l;){
            const action = outline[i++];
            switch(action){
                case 'm':
                    x = outline[i++] * scale + offsetX;
                    y = outline[i++] * scale + offsetY;
                    path.moveTo(x, y);
                    break;
                case 'l':
                    x = outline[i++] * scale + offsetX;
                    y = outline[i++] * scale + offsetY;
                    path.lineTo(x, y);
                    break;
                case 'q':
                    cpx = outline[i++] * scale + offsetX;
                    cpy = outline[i++] * scale + offsetY;
                    cpx1 = outline[i++] * scale + offsetX;
                    cpy1 = outline[i++] * scale + offsetY;
                    path.quadraticCurveTo(cpx1, cpy1, cpx, cpy);
                    break;
                case 'b':
                    cpx = outline[i++] * scale + offsetX;
                    cpy = outline[i++] * scale + offsetY;
                    cpx1 = outline[i++] * scale + offsetX;
                    cpy1 = outline[i++] * scale + offsetY;
                    cpx2 = outline[i++] * scale + offsetX;
                    cpy2 = outline[i++] * scale + offsetY;
                    path.bezierCurveTo(cpx1, cpy1, cpx2, cpy2, cpx, cpy);
                    break;
            }
        }
    }
    return {
        offsetX: glyph.ha * scale,
        path: path
    };
}
;
}),
"[project]/node_modules/three/examples/jsm/renderers/CSS2DRenderer.js [app-client] (ecmascript)", ((__turbopack_context__) => {
"use strict";

__turbopack_context__.s([
    "CSS2DObject",
    ()=>CSS2DObject,
    "CSS2DRenderer",
    ()=>CSS2DRenderer
]);
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$three$2f$build$2f$three$2e$core$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/node_modules/three/build/three.core.js [app-client] (ecmascript)");
;
/**
 * The only type of 3D object that is supported by {@link CSS2DRenderer}.
 *
 * @augments Object3D
 * @three_import import { CSS2DObject } from 'three/addons/renderers/CSS2DRenderer.js';
 */ class CSS2DObject extends __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$three$2f$build$2f$three$2e$core$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["Object3D"] {
    /**
	 * Constructs a new CSS2D object.
	 *
	 * @param {HTMLElement} [element] - The DOM element.
	 */ constructor(element = document.createElement('div')){
        super();
        /**
		 * This flag can be used for type testing.
		 *
		 * @type {boolean}
		 * @readonly
		 * @default true
		 */ this.isCSS2DObject = true;
        /**
		 * The DOM element which defines the appearance of this 3D object.
		 *
		 * @type {HTMLElement}
		 * @readonly
		 * @default true
		 */ this.element = element;
        this.element.style.position = 'absolute';
        this.element.style.userSelect = 'none';
        this.element.setAttribute('draggable', false);
        /**
		 * The 3D objects center point.
		 * `( 0, 0 )` is the lower left, `( 1, 1 )` is the top right.
		 *
		 * @type {Vector2}
		 * @default (0.5,0.5)
		 */ this.center = new __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$three$2f$build$2f$three$2e$core$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["Vector2"](0.5, 0.5);
        this.addEventListener('removed', function() {
            this.traverse(function(object) {
                if (object.element && object.element instanceof object.element.ownerDocument.defaultView.Element && object.element.parentNode !== null) {
                    object.element.remove();
                }
            });
        });
    }
    copy(source, recursive) {
        super.copy(source, recursive);
        this.element = source.element.cloneNode(true);
        this.center = source.center;
        return this;
    }
}
//
const _vector = new __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$three$2f$build$2f$three$2e$core$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["Vector3"]();
const _viewMatrix = new __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$three$2f$build$2f$three$2e$core$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["Matrix4"]();
const _viewProjectionMatrix = new __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$three$2f$build$2f$three$2e$core$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["Matrix4"]();
const _a = new __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$three$2f$build$2f$three$2e$core$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["Vector3"]();
const _b = new __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$three$2f$build$2f$three$2e$core$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["Vector3"]();
/**
 * This renderer is a simplified version of {@link CSS3DRenderer}. The only transformation that is
 * supported is translation.
 *
 * The renderer is very useful if you want to combine HTML based labels with 3D objects. Here too,
 * the respective DOM elements are wrapped into an instance of {@link CSS2DObject} and added to the
 * scene graph. All other types of renderable 3D objects (like meshes or point clouds) are ignored.
 *
 * `CSS2DRenderer` only supports 100% browser and display zoom.
 *
 * @three_import import { CSS2DRenderer } from 'three/addons/renderers/CSS2DRenderer.js';
 */ class CSS2DRenderer {
    /**
	 * Constructs a new CSS2D renderer.
	 *
	 * @param {CSS2DRenderer~Parameters} [parameters] - The parameters.
	 */ constructor(parameters = {}){
        const _this = this;
        let _width, _height;
        let _widthHalf, _heightHalf;
        const cache = {
            objects: new WeakMap()
        };
        const domElement = parameters.element !== undefined ? parameters.element : document.createElement('div');
        domElement.style.overflow = 'hidden';
        /**
		 * The DOM where the renderer appends its child-elements.
		 *
		 * @type {HTMLElement}
		 */ this.domElement = domElement;
        /**
		 * Controls whether the renderer assigns `z-index` values to CSS2DObject DOM elements.
		 * If set to `true`, z-index values are assigned first based on the `renderOrder`
		 * and secondly - the distance to the camera. If set to `false`, no z-index values are assigned.
		 *
		 * @type {boolean}
		 * @default true
		 */ this.sortObjects = true;
        /**
		 * Returns an object containing the width and height of the renderer.
		 *
		 * @return {{width:number,height:number}} The size of the renderer.
		 */ this.getSize = function() {
            return {
                width: _width,
                height: _height
            };
        };
        /**
		 * Renders the given scene using the given camera.
		 *
		 * @param {Object3D} scene - A scene or any other type of 3D object.
		 * @param {Camera} camera - The camera.
		 */ this.render = function(scene, camera) {
            if (scene.matrixWorldAutoUpdate === true) scene.updateMatrixWorld();
            if (camera.parent === null && camera.matrixWorldAutoUpdate === true) camera.updateMatrixWorld();
            _viewMatrix.copy(camera.matrixWorldInverse);
            _viewProjectionMatrix.multiplyMatrices(camera.projectionMatrix, _viewMatrix);
            renderObject(scene, scene, camera);
            if (this.sortObjects) zOrder(scene);
        };
        /**
		 * Resizes the renderer to the given width and height.
		 *
		 * @param {number} width - The width of the renderer.
		 * @param {number} height - The height of the renderer.
		 */ this.setSize = function(width, height) {
            _width = width;
            _height = height;
            _widthHalf = _width / 2;
            _heightHalf = _height / 2;
            domElement.style.width = width + 'px';
            domElement.style.height = height + 'px';
        };
        function hideObject(object) {
            if (object.isCSS2DObject) object.element.style.display = 'none';
            for(let i = 0, l = object.children.length; i < l; i++){
                hideObject(object.children[i]);
            }
        }
        function renderObject(object, scene, camera) {
            if (object.visible === false) {
                hideObject(object);
                return;
            }
            if (object.isCSS2DObject) {
                _vector.setFromMatrixPosition(object.matrixWorld);
                _vector.applyMatrix4(_viewProjectionMatrix);
                const visible = _vector.z >= -1 && _vector.z <= 1 && object.layers.test(camera.layers) === true;
                const element = object.element;
                element.style.display = visible === true ? '' : 'none';
                if (visible === true) {
                    object.onBeforeRender(_this, scene, camera);
                    element.style.transform = 'translate(' + -100 * object.center.x + '%,' + -100 * object.center.y + '%)' + 'translate(' + (_vector.x * _widthHalf + _widthHalf) + 'px,' + (-_vector.y * _heightHalf + _heightHalf) + 'px)';
                    if (element.parentNode !== domElement) {
                        domElement.appendChild(element);
                    }
                    object.onAfterRender(_this, scene, camera);
                }
                const objectData = {
                    distanceToCameraSquared: getDistanceToSquared(camera, object)
                };
                cache.objects.set(object, objectData);
            }
            for(let i = 0, l = object.children.length; i < l; i++){
                renderObject(object.children[i], scene, camera);
            }
        }
        function getDistanceToSquared(object1, object2) {
            _a.setFromMatrixPosition(object1.matrixWorld);
            _b.setFromMatrixPosition(object2.matrixWorld);
            return _a.distanceToSquared(_b);
        }
        function filterAndFlatten(scene) {
            const result = [];
            scene.traverseVisible(function(object) {
                if (object.isCSS2DObject) result.push(object);
            });
            return result;
        }
        function zOrder(scene) {
            const sorted = filterAndFlatten(scene).sort(function(a, b) {
                if (a.renderOrder !== b.renderOrder) {
                    return b.renderOrder - a.renderOrder;
                }
                const distanceA = cache.objects.get(a).distanceToCameraSquared;
                const distanceB = cache.objects.get(b).distanceToCameraSquared;
                return distanceA - distanceB;
            });
            const zMax = sorted.length;
            for(let i = 0, l = sorted.length; i < l; i++){
                sorted[i].element.style.zIndex = zMax - i;
            }
        }
    }
}
;
}),
]);

//# sourceMappingURL=node_modules_three_examples_jsm_15bbcbe5._.js.map