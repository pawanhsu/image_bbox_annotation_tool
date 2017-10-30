var svg_width = 720;
var svg_height = 480;
var deleted_box_id = []



d3.select(svg).attr('width', svg_width)
d3.select(svg).attr('height',svg_height)



function renderImage(){

  var canvas = $('#img-layer').drawImage({
    source: "{{url_for('static', filename= 'data/' + task_path + '/' + frame.frame_name) }}",
    x: 0,
    y: 0,
    fromCenter: false
    });
  console.log("Render Image!");

  //wait(1000);
  //callback.call();
}

function renderBboxes(){

  function loadBboxes(){
    results = [];
    bboxes = $('.bbox');

    for (i = 0; i<bboxes.length; i++){
      bbox = bboxes[i]
      id   = parseInt(bbox.getAttribute('id'))
      xmin = parseInt(bbox.getAttribute('xmin'));
      ymin = parseInt(bbox.getAttribute('ymin'));
      width = parseInt(bbox.getAttribute('width'));
      height = parseInt(bbox.getAttribute('height'));
      label = bbox.getAttribute('label');
      results.push({"x":xmin, "y":ymin, "width":width, "height":height, "label":label, "id":id});
    }
    return results;
    }
    boxes = loadBboxes();
    for(i=0;i<boxes.length;i++){
      new Rectangle(true,boxes[i]);
    }
}


d3.selectAll('.newbox').on('click', function(){ new Rectangle( null, null, label = d3.select(this).text());});

d3.select('#submit').on('click', function(){
  var boxes = new Array();
  d3.selectAll('rect.bbox').each(function(){
    var box = {};
    var rect = d3.select(this)
    box['id']     = rect.attr('id');
    box['xmin']   = rect.attr('x') / xAxis_scale;
    box['ymin']   = rect.attr('y') / yAxis_scale;
    box['width']  = rect.attr('width') / xAxis_scale;
    box['height'] = rect.attr('height') / yAxis_scale;
    box['label']  = rect.attr('label');
    if(rect.classed("dirty")){
      box['dirty'] = true;
    } else{
      box['dirty'] = false;
    }
    boxes.push(box);
  })
  boxes = JSON.stringify(boxes);
  d3.select('#boxes_info').attr('value',boxes);
  d3.select('#deleted_box_id').attr('value',JSON.stringify(deleted_box_id));
})


var w = 600, h = 500;
var svg = d3.select('svg');

var focus_box = false;

d3.select("body").on('keydown',function(d){

  if(focus_box){
    var rect = d3.select(focus_box.rectangleElement[0][0]);
    deleted_box_id.push(parseInt(rect.attr('id')));
    for (var property in focus_box) {
        if (focus_box.hasOwnProperty(property)) {
          if(property!= 'rectData')
            focus_box[property].remove();
        }
    }
    focus_box = false;
  }
});




function Rectangle(preloaded = false, box = [], label = '') {

    var self = this, rect, rectData = [], isDown = false, m1, m2, isDrag = false;
    var focus = false;

    var dragR = d3.behavior.drag().on('drag', dragRect);

    function dragRect() {
        if(!focus_box || focus){
          var e = d3.event;
          for(var i = 0; i < self.rectData.length; i++){
              d3.select(self.rectangleElement[0][0])
                  .attr('x', self.rectData[i].x += e.dx )
                  .attr('y', self.rectData[i].y += e.dy );
          }
          rect.style('cursor', 'move');
          updateRect();
          d3.select(this).classed('dirty',true);
        }
    }

    var dragC1 = d3.behavior.drag().on('drag', dragPoint1);
    var dragC2 = d3.behavior.drag().on('drag', dragPoint2);
    var dragC3 = d3.behavior.drag().on('drag', dragPoint3);
    var dragC4 = d3.behavior.drag().on('drag', dragPoint4);


    function dragPoint1() {
        if(!focus_box || focus){
          var e = d3.event;
          d3.select(self.pointElement1[0][0])
              .attr('cx', function(d) { return d.x += e.dx })
              .attr('cy', function(d) { return d.y += e.dy });
          updateRect();
          d3.select(this).classed('dirty',true);
        }
    }

    function dragPoint2() {
        if(!focus_box || focus){
          var e = d3.event;
          d3.select(self.pointElement2[0][0])
              .attr('cx', self.rectData[1].x += e.dx )
              .attr('cy', self.rectData[1].y += e.dy );
          updateRect();
          d3.select(this).classed('dirty',true);
        }
    }

    function dragPoint3() {
        if(!focus_box || focus){
          var e = d3.event;
          d3.select(self.pointElement3[0][0])
              .attr('cx', self.rectData[1].x += e.dx )
              .attr('cy', self.rectData[0].y += e.dy );
          updateRect();
          d3.select(this).classed('dirty',true);
        }
    }

    function dragPoint4() {
        if(!focus_box || focus){
          var e = d3.event;
          d3.select(self.pointElement4[0][0])
              .attr('cx', self.rectData[0].x += e.dx )
              .attr('cy', self.rectData[1].y += e.dy );
          updateRect();
          d3.select(this).classed('dirty',true);
        }
    }



    if(!preloaded){
      svg.on('mousedown', function() {
          m1 = d3.mouse(this);
          if (!isDown && !isDrag) {
              self.rectData = [ { x: m1[0], y: m1[1] }, { x: m1[0], y: m1[1] } ];
              initialBox(m1,m2,label,-1);
              updateRect();

              isDrag = false;
          } else {
              isDrag = true;
          }
          isDown = !isDown;
      })
      svg.on('mousemove', function() {
          m2 = d3.mouse(this);
          if(isDown && !isDrag) {
              self.rectData[1] = { x: m2[0], y: m2[1] };
              updateRect();
          }
      });
  }
  else{
      m1 = [box.x * xAxis_scale, box.y * yAxis_scale], m2 = [(box.x + box.width)  * xAxis_scale, (box.y + box.height) * yAxis_scale];
      initialBox(m1,m2,box.label,box.id);
      updateRect();
  }

  function initialBox(m1,m2,label, id){
    self.rectData = [ { x: m1[0], y: m1[1] }, { x: m2[0], y: m2[1] } ];
    self.rectangleElement = d3.select('svg').append('rect').attr({
      class: 'bbox',
      id   : id,
      label: label
    }).call(dragR);
    self.pointElement1 = d3.select('svg').append('circle').attr('class', 'pointC').call(dragC1);
    self.pointElement2 = d3.select('svg').append('circle').attr('class', 'pointC').call(dragC2);
    self.pointElement3 = svg.append('circle').attr('class', 'pointC').call(dragC3);
    self.pointElement4 = svg.append('circle').attr('class', 'pointC').call(dragC4);
    self.Label         = svg.append('rect').attr('class','Label')
    self.text          = svg.append('text').text(label)
    self.rectangleElement.on('dblclick',focusBox);
  }

  function focusBox(){
    var e = d3.event;
    rect = d3.select(self.rectangleElement[0][0]);
    if(focus){
      rect.style('fill','none');
      console.log('box focus');
      focus_box = false;
      focus = !focus;
    } else if(!focus_box){
      rect.style('fill','rgba(0,255,0,0.1)');
      focus_box = self;
      focus = !focus;
    }
  }

  function updateRect() {
      rect = d3.select(self.rectangleElement[0][0]);
      rect.attr({
          x: self.rectData[1].x - self.rectData[0].x > 0 ? self.rectData[0].x :  self.rectData[1].x,
          y: self.rectData[1].y - self.rectData[0].y > 0 ? self.rectData[0].y :  self.rectData[1].y,
          width: Math.abs(self.rectData[1].x - self.rectData[0].x),
          height: Math.abs(self.rectData[1].y - self.rectData[0].y),
      });

      var text   = d3.select(self.text[0][0]).data(self.rectData);
      text.attr({
        x: self.rectData[0].x+10,
        y: self.rectData[0].y-5,
      }).style("font-size", "20px")

      var label  = d3.select(self.Label[0][0]).data(self.rectData);
      label.attr({
        x: self.rectData[0].x,
        y: self.rectData[0].y-23,
        width: Math.abs(self.rectData[1].x - self.rectData[0].x),
        height: 20
      }).style('fill','green')

      var point1 = d3.select(self.pointElement1[0][0]).data(self.rectData);
      point1.attr('r', 2)
            .attr('cx', self.rectData[0].x)
            .attr('cy', self.rectData[0].y);
      var point2 = d3.select(self.pointElement2[0][0]).data(self.rectData);
      point2.attr('r', 2)
            .attr('cx', self.rectData[1].x)
            .attr('cy', self.rectData[1].y);
      var point3 = d3.select(self.pointElement3[0][0]).data(self.rectData);
      point3.attr('r', 2)
            .attr('cx', self.rectData[1].x)
            .attr('cy', self.rectData[0].y);
      var point3 = d3.select(self.pointElement4[0][0]).data(self.rectData);
      point3.attr('r', 2)
            .attr('cx', self.rectData[0].x)
            .attr('cy', self.rectData[1].y);
  }


}//end Rectangle



renderBboxes()
