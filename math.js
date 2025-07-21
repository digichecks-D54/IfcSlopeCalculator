function getPolylineArea(coo){
    var a=0
    for(let i=0;i<coo.length-1;i++){
        a += coo[i][0]*coo[i+1][1]-coo[i+1][0]*coo[i][1]
    }
    a += coo[coo.length-1][0]*coo[0][1]-coo[0][0]*coo[coo.length-1][1]
    a=a/2
    //console.log("area: " + a)
    return a
}


module.exports = {getPolylineArea};