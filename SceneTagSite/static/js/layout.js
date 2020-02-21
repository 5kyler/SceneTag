function create_canvasTag(root, id, width, height, style) {
    var temp = root.append("div")
    temp.append("canvas").attr("id",id).attr("width",width).attr("height",height).attr("style",style)
}