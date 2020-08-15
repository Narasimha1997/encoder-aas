import sentencepiece as sp


def process_to_IDs_in_sparse_format(sp, sentences):
  # An utility method that processes sentences with the sentence piece processor
  # 'sp' and returns the results in tf.SparseTensor-similar format:
  # (values, indices, dense_shape)
  ids = [sp.EncodeAsIds(x) for x in sentences]
  max_len = max(len(x) for x in ids)
  dense_shape=(len(ids), max_len)
  values=[item for sublist in ids for item in sublist]
  indices=[[row,col] for row in range(len(ids)) for col in range(len(ids[row]))]
  return (values, indices, dense_shape)

class SparseEncoder :

    def __init__(self, model_path = "model/assets/universal_encoder_8k_spm.model"):
        self.processor = sp.SentencePieceProcessor()
        self.processor.Load(model_path)
    
    def getSparseEncodings(self, sentences) :
        return process_to_IDs_in_sparse_format(self.processor, sentences)

