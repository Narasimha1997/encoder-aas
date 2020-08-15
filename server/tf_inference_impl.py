import tensorflow as tf 


class EmbeddingGenerationEngine :

    def __init__(self, model_path = "model", device = 'cpu') :

        self.session = tf.Session()
        self.model = tf.saved_model.load(self.session, [], model_path)
        self.model = self.model.signature_def['default']

        self.graph = tf.get_default_graph()

        self.outputNode = self.graph.get_tensor_by_name('Encoder_en/hidden_layers/l2_normalize:0')
        self.input_values = self.graph.get_tensor_by_name('Placeholder_1:0')
        self.input_indices = self.graph.get_tensor_by_name('Placeholder_2:0')
        self.input_dense_shapes = self.graph.get_tensor_by_name('Placeholder:0')
    
    def infer(self, values, indices, dense_shape) :
        print('called infer')

        outputs = self.session.run(
            self.outputNode, 
            {
                self.input_values: values,
                self.input_indices: indices,
                self.input_dense_shapes: dense_shape
            }
        )

        return outputs


