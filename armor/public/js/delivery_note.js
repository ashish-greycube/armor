{% include 'armor/public/js/sales_armor_common.js' %}

var sourceImage ;
var targetRoot;
var maState;

frappe.ui.form.on("Delivery Note", {
  refresh: function (frm) {
    if (frm.doc.doctype=='Delivery Note') {
      let color_df = frappe.meta.get_docfield("Car Information CT","color", frm.doc.name);
      let km_df = frappe.meta.get_docfield("Car Information CT","km", frm.doc.name);
      let plate_no_df = frappe.meta.get_docfield("Car Information CT","plate_no", frm.doc.name);

      color_df.reqd = 1;      
      km_df.reqd = 1;   
      plate_no_df.reqd = 1;   
    }
  },
	onload_post_render: function(frm) {
    $(frm.fields_dict['car_structure_html'].wrapper)
    .html('<div  style="position: relative; display: flex;flex-direction: column;align-items: center;justify-content: center;padding-top: 50px;"> \
    <img  id="sourceImage"   src="/assets/armor/image/car_structure.png" style="max-width: 900px; max-height: 80%;"  crossorigin="anonymous" /> \
    <img  id="sampleImage"   src="/assets/armor/image/car_structure.png"  style="max-width: 900px; max-height: 100%; position: absolute;" crossorigin="anonymous" /> \
    </div>');

    setSourceImage(document.getElementById("sourceImage"));

    const sampleImage = document.getElementById("sampleImage");
    sampleImage.addEventListener("click", () => {
      showMarkerArea(sampleImage);
    });      
  }
})

function setSourceImage(source) {
  sourceImage = source;
  targetRoot = source.parentElement;
}

function showMarkerArea(target) {
  const markerArea = new markerjs2.MarkerArea(sourceImage);
    markerArea.renderImageQuality = 0.5;
    markerArea.renderImageType = 'image/jpeg';

  // since the container div is set to position: relative it is now our positioning root
  // end we have to let marker.js know that
  markerArea.targetRoot = targetRoot;
  markerArea.addRenderEventListener((imgURL, state) => {
    target.src = imgURL;
    // save the state of MarkerArea
    cur_frm.doc.car_structure_annotation=JSON.stringify(state)
   
    cur_frm.set_value('annotated_car_image_cf', imgURL)
    cur_frm.save()
  });
  markerArea.show();
  // if previous state is present - restore it
  if (cur_frm.doc.car_structure_annotation) {
    markerArea.restoreState(JSON.parse(cur_frm.doc.car_structure_annotation));
  }
}