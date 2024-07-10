kernel df_StructureTensor : ImageComputationKernel<ePixelWise>
{
    Image<eRead, eAccessRandom, eEdgeClamped> src; 
    Image<eWrite> dst; 

/*  
 *  Blink C++ implementation by Derek Flood, 2024
 *
 *  Adapted from the Blender GLSL script (Copyright: 2023 Blender Authors)
 *  https://projects.blender.org/blender/blender/src/source/blender/compositor/realtime_compositor/shaders/
 *     compositor_kuwahara_anisotropic_compute_structure_tensor.glsl
 *   ---------------------------------------------- 
 *  
 *  Computes the structure tensor of the image using a Dirac delta window function as described in
 *  section "3.2 Local Structure Estimation" of the paper: Kyprianidis, Jan Eric. 
 * "Image and video abstraction by multi-scale anisotropic Kuwahara filtering." 2011.
 *  
 *  The structure tensor should then be smoothed using a Gaussian function to eliminate high frequency details.
 */

    void process(int2 pos) {
        SampleType(src) input = src(pos.x, pos.y);

  		// The weight kernels of the filter optimized for rotational symmetry 
  		// described in section "3.2.1 Gradient Calculation".
		const float corner_weight = 0.182f;
        const float center_weight = 1.0f - 2.0f * corner_weight;

        float4 x_partial_derivative = src(pos.x - 1, pos.y + 1) * -corner_weight +                      
                                        src(pos.x - 1, pos.y    ) * -center_weight +
                                        src(pos.x - 1, pos.y - 1) * -corner_weight +
                                        src(pos.x + 1, pos.y + 1) * corner_weight +
                                        src(pos.x + 1, pos.y    ) * center_weight +
                                        src(pos.x + 1, pos.y - 1) * corner_weight;

    	float4 y_partial_derivative = src(pos.x - 1, pos.y + 1) * corner_weight +
                                        src(pos.x    , pos.y + 1) * center_weight +
                                        src(pos.x + 1, pos.y + 1) * corner_weight +
                                        src(pos.x - 1, pos.y - 1) * -corner_weight +
                                        src(pos.x    , pos.y - 1) * -center_weight +
                                        src(pos.x + 1, pos.y - 1) * -corner_weight;

        float dxdx = dot(x_partial_derivative, x_partial_derivative);
        float dxdy = dot(x_partial_derivative, y_partial_derivative);
        float dydy = dot(y_partial_derivative, y_partial_derivative);
        
  		dst(0) = dxdx;
  		dst(1) = dxdy;
  		dst(2) = dydy;
	}
};
