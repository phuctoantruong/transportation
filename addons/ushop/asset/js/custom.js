$(document).ready(function(){
	$(document).on("change","select[name='country_id']",function() {
	    return $.ajax({
	    	url: "/shop/checkout/changeCountry",
	    	method: "GET",
	    	data: {country_id: $("select[name='country_id']").val()},
	    	datatype: "JSON",
	    	success: function(data){
	    		data = JSON.parse(data)
	    		$("select[name='city_id']").find("option").remove();
	    		$("select[name='district_id']").find("option").remove();
	    		$("select[name='ward_id']").find("option").remove();
	    		$("input[name='street']").val("");
	    		var selectcity = $("select[name='city_id']");
	    		$("<option>").val("").text("City...").appendTo($(selectcity));
	    		for(i = 0; i < data.length; i++){
					$("<option>").val(data[i].id).text(data[i].name).appendTo($(selectcity));
				}
	    		
	    	}
	    });
	 });
	$(document).on("change","select[name='shipping_country_id']",function() {
	    return $.ajax({
	    	url: "/shop/checkout/changeCountry",
	    	method: "GET",
	    	data: {country_id: $("select[name='shipping_country_id']").val()},
	    	datatype: "JSON",
	    	success: function(data){
	    		data = JSON.parse(data)
	    		$("select[name='shipping_city_id']").find("option").remove();
	    		$("select[name='shipping_district_id']").find("option").remove();
	    		$("select[name='shipping_ward_id']").find("option").remove();
	    		$("input[name='shipping_street']").val("");
	    		var selectcity = $("select[name='shipping_city_id']");
	    		$("<option>").val("").text("City...").appendTo($(selectcity));
	    		for(i = 0; i < data.length; i++){
					$("<option>").val(data[i].id).text(data[i].name).appendTo($(selectcity));
				}
	    		
	    	}
	    });
	 });
})	
	function changeCity() {
	    return $.ajax({
	    	url: "/shop/checkout/changeCity",
	    	method: "GET",
	    	data: {city_id: $("select[name='city_id']").val()},
	    	datatype: "JSON",
	    	success: function(data){
	    		data = JSON.parse(data)
	    		$("select[name='district_id']").find("option").remove();
	    		var selectdistrict = $("select[name='district_id']");
	    		$("select[name='ward_id']").find("option").remove();
	    		$("input[name='street']").val("");
	    		$("<option>").val("").text("District...").appendTo($(selectdistrict));
	    		for(i = 0; i < data.length; i++){
					$("<option>").val(data[i].id).text(data[i].name).appendTo($(selectdistrict));
				}
	    		
	    	}
	    });
	 };
	 function changeDistrict() {
	    return $.ajax({
	    	url: "/shop/checkout/changeDistrict",
	    	method: "GET",
	    	data: {district_id: $("select[name='district_id']").val()},
	    	datatype: "JSON",
	    	success: function(data){
	    		data = JSON.parse(data)
	    		$("select[name='ward_id']").find("option").remove();
	    		$("input[name='street']").val("");
	    		var selectward = $("select[name='ward_id']");
	    		$("<option>").val("").text("Ward...").appendTo($(selectward));
	    		for(i = 0; i < data.length; i++){
					$("<option>").val(data[i].id).text(data[i].name).appendTo($(selectward));
				}
	    		
	    	}
	    });
	 };
	 function changeShippingCity() {
		    return $.ajax({
		    	url: "/shop/checkout/changeCity",
		    	method: "GET",
		    	data: {city_id: $("select[name='shipping_city_id']").val()},
		    	datatype: "JSON",
		    	success: function(data){
		    		data = JSON.parse(data)
		    		$("select[name='shipping_district_id']").find("option").remove();
		    		var selectdistrict = $("select[name='shipping_district_id']");
		    		$("select[name='shipping_ward_id']").find("option").remove();
		    		$("input[name='shipping_street']").val("");
		    		$("<option>").val("").text("District...").appendTo($(selectdistrict));
		    		for(i = 0; i < data.length; i++){
						$("<option>").val(data[i].id).text(data[i].name).appendTo($(selectdistrict));
					}
		    		
		    	}
		    });
		 };
		 function changeShippingDistrict() {
		    return $.ajax({
		    	url: "/shop/checkout/changeDistrict",
		    	method: "GET",
		    	data: {district_id: $("select[name='shipping_district_id']").val()},
		    	datatype: "JSON",
		    	success: function(data){
		    		data = JSON.parse(data)
		    		$("select[name='shipping_ward_id']").find("option").remove();
		    		$("input[name='shipping_street']").val("");
		    		var selectward = $("select[name='shipping_ward_id']");
		    		$("<option>").val("").text("Ward...").appendTo($(selectward));
		    		for(i = 0; i < data.length; i++){
						$("<option>").val(data[i].id).text(data[i].name).appendTo($(selectward));
					}
		    		
		    	}
		    });
		 };