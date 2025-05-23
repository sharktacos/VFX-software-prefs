kernel df_KuwaharaAnisotropic : ImageComputationKernel<ePixelWise>
{

/*  
 *  Blink C++ implementation by Derek Flood, 2024
 *
 *  Adapted from the Blender GLSL script (Copyright: 2023 Blender Authors)
 *  https://projects.blender.org/blender/blender/src/source/blender/compositor/realtime_compositor/shaders/
 *  compositor_kuwahara_anisotropic.glsl
 *   ---------------------------------------------- 
 *
 *  An implementation of the Anisotropic Kuwahara filter described in the paper:
 *   Kyprianidis, Jan Eric, Henry Kang, and Jurgen Dollner. "Image and video abstraction by
 *   anisotropic Kuwahara filtering." 2009.
 *
 *  But with the polynomial weighting functions described in the paper:
 *   Kyprianidis, Jan Eric, et al. "Anisotropic Kuwahara Filtering with Polynomial Weighting
 *   Functions." 2010.
 *
 *  And the sector weight function described in the paper:
 *  Kyprianidis, Jan Eric. "Image and video abstraction by multi-scale anisotropic Kuwahara
 *  filtering." 2011.
 */ 
 
    Image<eRead, eAccessRandom, eEdgeClamped> src; 
    Image<eRead, eAccessRandom, eEdgeClamped> structure_tensor;
    Image<eRead, eAccessRandom> radius_map;  // for mapped radius
    Image<eWrite> dst; 
    
    param:
        float size; 
        float sharpness;
        float eccentricity;

    void define() {
        defineParam(size, "Size", 10.0f); 
        defineParam(sharpness, "Sharpness", 1.0f); 
        defineParam(eccentricity, "Eccentricity", 0.5f); 
    }
    
    inline float square(float x) {
  		return x * x;
	}
	


    void process(int2 pos) {
          		
  		// The structure tensor is encoded in a float4 using a column major storage order, as can be seen
		// in the compositor_kuwahara_anisotropic_compute_structure_tensor.glsl shader. 
		float4 encoded_structure_tensor = structure_tensor (pos.x, pos.y);
		
		float dxdx = encoded_structure_tensor.x;
		float dxdy = encoded_structure_tensor.y;
		float dydy = encoded_structure_tensor.z;
  		

		// Compute the first and second eigenvalues of the structure tensor using the equations in
		// section "3.1 Orientation and Anisotropy Estimation" of the paper. 
		float eigenvalue_first_term = (dxdx + dydy) / 2.f;
  		float eigenvalue_square_root_term = sqrt(square(dxdx - dydy) + 4.0f * square(dxdy)) / 2.0f;
		float first_eigenvalue = eigenvalue_first_term + eigenvalue_square_root_term;
		float second_eigenvalue = eigenvalue_first_term - eigenvalue_square_root_term;

		// Compute the normalized eigenvector of the structure tensor oriented in direction of the
		// minimum rate of change using the equations in section "3.1 Orientation and Anisotropy
		// Estimation" of the paper. 
		float2 eigenvector = float2(first_eigenvalue - dxdx, -1.0f * dxdy);
		float eigenvector_length = length(eigenvector);
		float2 unit_eigenvector = eigenvector_length != 0.0f ? eigenvector / eigenvector_length : float2(1.0f);

		// Compute the amount of anisotropy using equations in section "3.1 Orientation and Anisotropy
		// Estimation" of the paper. The anisotropy ranges from 0 to 1, where 0 corresponds to isotropic
		// and 1 corresponds to entirely anisotropic regions. 
		float eigenvalue_sum = first_eigenvalue + second_eigenvalue;
		float eigenvalue_difference = first_eigenvalue - second_eigenvalue;
		float anisotropy = eigenvalue_sum > 0.0f ? eigenvalue_difference / eigenvalue_sum : 0.0f;
		
		// Map radius
		float alpha = radius_map(pos.x, pos.y).w;
		float radius = alpha * size;
			
		if (radius == 0.0f) {
				dst() = src (pos.x, pos.y);
		  return;
		}


		// Compute the width and height of an ellipse that is more width-elongated for high anisotropy
		// and more circular for low anisotropy, controlled using the eccentricity factor. Since the
		// anisotropy is in the [0, 1] range, the width factor tends to 1 as the eccentricity tends to
		// infinity and tends to infinity when the eccentricity tends to zero. This is based on the
		// equations in section "3.2. Anisotropic Kuwahara Filtering" of the paper. 
		float eccentricity_clamp = min(eccentricity, 0.95f);
		float eccentric_adj = (1.0f - eccentricity_clamp) * 10.f;
		float ellipse_width_factor = (eccentric_adj + anisotropy) / eccentric_adj;

		float ellipse_width = ellipse_width_factor * radius;
		float ellipse_height = radius / ellipse_width_factor;

		// Compute the cosine and sine of the angle that the eigenvector makes with the x axis. Since the
		// eigenvector is normalized, its x and y components are the cosine and sine of the angle it
		// makes with the x axis. 
		float cosine = unit_eigenvector.x;
		float sine = unit_eigenvector.y;

		// Compute an inverse transformation matrix that represents an ellipse of the given width and
		// height and makes and an angle with the x axis of the given cosine and sine. This is an inverse
		// matrix, so it transforms the ellipse into a disk of unit radius. 
		float2 inverse_ellipse_matrix_1 (cosine / ellipse_width,     sine / ellipse_width);
        float2 inverse_ellipse_matrix_2 (-sine / ellipse_height,     cosine / ellipse_height); 

		// Compute the bounding box of a zero centered ellipse whose major axis is aligned with the
		// eigenvector and has the given width and height. This is based on the equations described in:
		//
		//   https://iquilezles.org/articles/ellipses/
		//
		// Notice that we only compute the upper bound, the lower bound is just negative that since the
		// ellipse is zero centered. Also notice that we take the ceiling of the bounding box, just to
		// ensure the filter window is at least 1x1. 
		float2 ellipse_major_axis = ellipse_width * unit_eigenvector;
		float2 ellipse_minor_axis = float2(ellipse_height * unit_eigenvector.y * -1.f,
                                    ellipse_height * unit_eigenvector.x * 1.f);

		int2 ellipse_bounds = int2(
    		ceil(sqrt( square(ellipse_major_axis.x) + square(ellipse_minor_axis.x) )),
    		ceil(sqrt( square(ellipse_major_axis.y) + square(ellipse_minor_axis.y) ))
		);


		// Compute the overlap polynomial parameters for 8-sector ellipse based on the equations in
		// section "3 Alternative Weighting Functions" of the polynomial weights paper. More on this
		// later in the code. 
		const int number_of_sectors = 8;
		float sector_center_overlap_parameter = 2.f / radius;
		float sector_envelope_angle = ((3.f / 2.f) * PI) / number_of_sectors;                          
        float cross_sector_overlap_parameter = (sector_center_overlap_parameter + 
        								cos(sector_envelope_angle)) /
                                        square( sin(sector_envelope_angle) );


		// We need to compute the weighted mean of color and squared color of each of the 8 sectors of
 		// the ellipse, so we declare arrays for accumulating those and initialize them in the next code
 		// section.
		float4 weighted_mean_of_squared_color_of_sectors[8];
		float4 weighted_mean_of_color_of_sectors[8];
		float sum_of_weights_of_sectors[8];

		// The center pixel (0, 0) is exempt from the main loop below for reasons that are explained in
 		// the first if statement in the loop, so we need to accumulate its color, squared color, and
 		// weight separately first. Luckily, the zero coordinates of the center pixel zeros out most of
 		// the complex computations below, and it can easily be shown that the weight for the center
 		// pixel in all sectors is simply (1 / number_of_sectors).
		float4 center_color = src (pos.x, pos.y); 		
		float4 center_color_squared = center_color * center_color;
		float center_weight_b = 1.f / number_of_sectors;
		float4 weighted_center_color = center_color * center_weight_b;
		float4 weighted_center_color_squared = center_color_squared * center_weight_b;

		for (int i = 0; i < number_of_sectors; i++) {
				weighted_mean_of_squared_color_of_sectors[i] = weighted_center_color_squared;
				weighted_mean_of_color_of_sectors[i] = weighted_center_color;
				sum_of_weights_of_sectors[i] = center_weight_b;
		}

		// Loop over the window of pixels inside the bounding box of the ellipse. However, we utilize the
 		// fact that ellipses are mirror symmetric along the horizontal axis, so we reduce the window to
 		// only the upper two quadrants, and compute each two mirrored pixels at the same time using the
 		// same weight as an optimization.
		for (int j = 0; j <= ellipse_bounds.y; j++) {
			for (int i = -ellipse_bounds.x; i <= ellipse_bounds.x; i++) {
				
    			// Since we compute each two mirrored pixels at the same time, we need to also exempt the
     			// pixels whose x coordinates are negative and their y coordinates are zero, that's because
     			// those are mirrored versions of the pixels whose x coordinates are positive and their y
     			// coordinates are zero, and we don't want to compute and accumulate them twice. Moreover, we
     			// also need to exempt the center pixel with zero coordinates for the same reason, however,
     			// since the mirror of the center pixel is itself, it need to be accumulated separately,
     			// hence why we did that in the code section just before this loop.
      			if (j == 0 && i <= 0) { 
      				continue;
      			}

    			// Map the pixels of the ellipse into a unit disk, exempting any points that are not part of
     			// the ellipse or disk.
     			float2 disk_point(
     					(inverse_ellipse_matrix_1.x * i + inverse_ellipse_matrix_1.y * j), 
     					(inverse_ellipse_matrix_2.x * i + inverse_ellipse_matrix_2.y * j)
     					);

      			float disk_point_length_squared = dot(disk_point, disk_point);
      			if (disk_point_length_squared > 1.0f) {
        			continue;
      			}

    			// While each pixel belongs to a single sector in the ellipse, we expand the definition of
     			// a sector a bit to also overlap with other sectors as illustrated in Figure 8 of the
     			// polynomial weights paper. So each pixel may contribute to multiple sectors, and thus we
     			// compute its weight in each of the 8 sectors.
      			float sector_weights[8];

    			// We evaluate the weighting polynomial at each of the 8 sectors by rotating the disk point
     			// by 45 degrees and evaluating the weighting polynomial at each incremental rotation. To
     			// avoid potentially expensive rotations, we utilize the fact that rotations by 90 degrees
     			// are simply swapping of the coordinates and negating the x component. We also note that
     			// since the y term of the weighting polynomial is squared, it is not affected by the sign
     			// and can be computed once for the x and once for the y coordinates. So we compute every
     			// other even-indexed 4 weights by successive 90 degree rotations as discussed.

      			float2 polynomial = sector_center_overlap_parameter -
                        cross_sector_overlap_parameter * disk_point * disk_point;
      			sector_weights[0] = square(max(0.f, disk_point.y + polynomial.x));
      			sector_weights[2] = square(max(0.f, -disk_point.x + polynomial.y));
      			sector_weights[4] = square(max(0.f, -disk_point.y + polynomial.x));
      			sector_weights[6] = square(max(0.f, disk_point.x + polynomial.y));

    			// Then we rotate the disk point by 45 degrees, which is a simple expression involving a
     			// constant as can be demonstrated by applying a 45 degree rotation matrix.
				float M_SQRT1_2 =  1.0f / sqrt(2.0f);  // M_SQRT1_2 = 0.70710678118654752440f  			
      			float2 rotated_disk_point = M_SQRT1_2 *
                                float2(disk_point.x - disk_point.y, disk_point.x + disk_point.y);


    			// Finally, we compute every other odd-index 4 weights starting from the 45 degrees rotated disk point.
      			float2 rotated_polynomial = sector_center_overlap_parameter -
                                cross_sector_overlap_parameter * rotated_disk_point * rotated_disk_point;
      			sector_weights[1] = square(max(0.f, rotated_disk_point.y + rotated_polynomial.x));
      			sector_weights[3] = square(max(0.f, -rotated_disk_point.x + rotated_polynomial.y));
      			sector_weights[5] = square(max(0.f, -rotated_disk_point.y + rotated_polynomial.x));
      			sector_weights[7] = square(max(0.f, rotated_disk_point.x + rotated_polynomial.y));


    			// We compute a radial Gaussian weighting component such that pixels further away from the
     			// sector center gets attenuated, and we also divide by the sum of sector weights to
     			// normalize them, since the radial weight will eventually be multiplied to the sector weight below.
      			float sector_weights_sum = sector_weights[0] + sector_weights[1] + sector_weights[2] +
                                 sector_weights[3] + sector_weights[4] + sector_weights[5] +
                                 sector_weights[6] + sector_weights[7];
      			float radial_gaussian_weight = exp(-PI * disk_point_length_squared) / sector_weights_sum;


    			// Load the color of the pixel and its mirrored pixel and compute their square.
      			float4 upper_color = src (pos.x + i, pos.y + j); 
      			float4 lower_color = src (pos.x - i, pos.y - j); 
      			float4 upper_color_squared = upper_color * upper_color;
      			float4 lower_color_squared = lower_color * lower_color;


      			for (int k = 0; k < number_of_sectors; k++) {
        			float weight = sector_weights[k] * radial_gaussian_weight;

      				// Accumulate the pixel to each of the sectors multiplied by the sector weight.
        			int upper_index = k;
        			sum_of_weights_of_sectors[upper_index] += weight;
        			weighted_mean_of_color_of_sectors[upper_index] += upper_color * weight;
        			weighted_mean_of_squared_color_of_sectors[upper_index] += upper_color_squared * weight;

      				// Accumulate the mirrored pixel to each of the sectors multiplied by the sector weight.
        			int lower_index = (k + number_of_sectors / 2) % number_of_sectors;
        			sum_of_weights_of_sectors[lower_index] += weight;
        			weighted_mean_of_color_of_sectors[lower_index] += lower_color * weight;
        			weighted_mean_of_squared_color_of_sectors[lower_index] += lower_color_squared * weight;
        		}
    		}
		}

		// Compute the weighted sum of mean of sectors, such that sectors with lower standard deviation
 		// gets more significant weight than sectors with higher standard deviation.
  		float sum_of_weights = 0.f;
  		float4 weighted_sum = float4(0.f);
  		for (int i = 0; i < number_of_sectors; i++) {
    		weighted_mean_of_color_of_sectors[i] /= sum_of_weights_of_sectors[i];
    		weighted_mean_of_squared_color_of_sectors[i] /= sum_of_weights_of_sectors[i];

    		float4 color_mean = weighted_mean_of_color_of_sectors[i];
    		float4 squared_color_mean = weighted_mean_of_squared_color_of_sectors[i];
    		float4 color_variance = fabs(squared_color_mean - color_mean * color_mean);

    		float standard_deviation = dot(sqrt(
    			float3(color_variance.x, color_variance.y, color_variance.z)), float3(1.0f));


  			// Compute the sector weight based on the weight function introduced in section "3.3.1
   			// Single-scale Filtering" of the multi-scale paper. Use a threshold of 0.02 to avoid zero
   			// division and avoid artifacts in homogeneous regions as demonstrated in the paper.
   			float normalized_sharpness = sharpness * 10.0f;
    		float weight = 1.0 / pow( max(0.02, standard_deviation), normalized_sharpness);

    		sum_of_weights += weight;
    		weighted_sum += color_mean * weight;
  		}

  		weighted_sum /= sum_of_weights;
  		//dst() = weighted_sum;
  		dst(0) = weighted_sum.x;
  		dst(1) = weighted_sum.y;
  		dst(2) = weighted_sum.z;
  		dst(3) = alpha;
	}
};
