frappe.ui.form.on('Lead', {
  email_id:function (frm) {
    if (frm.doc.email_id==undefined || frm.doc.email_id=='') {
      frappe.throw({message:__("Email id is mandatory."),title:__("Email id is missing." )})
    }   
  },
  refresh:function (frm) {
    frm.set_df_property('email_id', 'reqd', 1)
  },
  validate:function (frm) {
    if (frm.doc.email_id==undefined || frm.doc.email_id=='') {
      frappe.throw({message:__("Email id is mandatory."),title:__("Email id is missing." )})
    }
  }
//   source: function (frm) {
//     if (frm.doc.source) {
//       let sales_partners = []
//       let lead_source_value = frm.doc.source
//       frappe.db.get_doc('Lead Source', lead_source_value)
//         .then(doc => {
//           if (doc.is_agency_cf == 1) {
//             $.each(doc.sales_partners_cf, function (index, source_row) {
//               sales_partners.push(source_row.sales_partner)
//             });
//             frm.set_query('sales_partner', () => {
//               return {
//                 filters: {
//                   partner_name: ['in', sales_partners]
//                 }
//               }
//             })
//             frm.toggle_reqd('sales_partner', doc.is_agency_cf);
//             frm.refresh_field('sales_partner')
//           } else if (doc.is_agency_cf == 0) {
//             frm.set_query('sales_partner', () => {
//               return {
//                 filters: {
//                   partner_name: ['in', sales_partners]
//                 }
//               }
//             })
//             frm.toggle_reqd('sales_partner', doc.is_agency_cf);
//             frm.refresh_field('sales_partner')
//           }
//         })
//     }
//   }
});