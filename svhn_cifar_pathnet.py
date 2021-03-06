from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import argparse
import sys,os,time
import subprocess
import scipy.io as sio
import tensorflow as tf
from six.moves import urllib

import cifar10
import pathnet

import numpy as np

FLAGS = None

def svhn_maybe_download_and_extract():
  """Download and extract the tarball from website ( http://ufldl.stanford.edu/housenumbers/ )."""
  """Copy the code from cifar10.py Tensorflow Example Code!!"""
  dest_directory = FLAGS.svhn_data_dir
  if not os.path.exists(dest_directory):
    os.makedirs(dest_directory)
  # Training Data
  DATA_URL = 'http://ufldl.stanford.edu/housenumbers/train_32x32.mat'
  filename = DATA_URL.split('/')[-1]
  filepath = os.path.join(dest_directory, filename)
  if not os.path.exists(filepath):
    def _progress(count, block_size, total_size):
      sys.stdout.write('\r>> Downloading %s %.1f%%' % (filename,
          float(count * block_size) / float(total_size) * 100.0))
      sys.stdout.flush()
    filepath, _ = urllib.request.urlretrieve(DATA_URL, filepath, _progress)
    print()
    statinfo = os.stat(filepath)
    print('Successfully downloaded', filename, statinfo.st_size, 'bytes.')
    
  # Test Data    
  DATA_URL = 'http://ufldl.stanford.edu/housenumbers/test_32x32.mat'
  filename = DATA_URL.split('/')[-1]
  filepath = os.path.join(dest_directory, filename)
  if not os.path.exists(filepath):
    def _progress(count, block_size, total_size):
      sys.stdout.write('\r>> Downloading %s %.1f%%' % (filename,
          float(count * block_size) / float(total_size) * 100.0))
      sys.stdout.flush()
    filepath, _ = urllib.request.urlretrieve(DATA_URL, filepath, _progress)
    print()
    statinfo = os.stat(filepath)
    print('Successfully downloaded', filename, statinfo.st_size, 'bytes.')
    

def train():
  # Get SVHN dataset
  svhn_maybe_download_and_extract();
  file_name=os.path.join(FLAGS.svhn_data_dir,"train_32x32.mat");
  train=sio.loadmat(file_name);
  tr_data_svhn=np.zeros((len(train['y']),32*32*3),dtype=float);
  tr_label_svhn=np.zeros((len(train['y']),10),dtype=float);
  for i in range(len(train['y'])):
    tr_data_svhn[i]=np.reshape(train['X'][:,:,:,i],[1,32*32*3]);
    tr_label_svhn[i,train['y'][i][0]-1]=1.0;
  tr_data_svhn=tr_data_svhn/255.0;  
  tr_label_svhn=np.zeros((len(train['y']),10),dtype=float);
  
  file_name=os.path.join(FLAGS.svhn_data_dir,"test_32x32.mat");
  test=sio.loadmat(file_name);
  ts_data_svhn=np.zeros((len(test['y']),32*32*3),dtype=float);
  ts_label_svhn=np.zeros((len(test['y']),10),dtype=float);
  for i in range(len(test['y'])):
    ts_data_svhn[i]=np.reshape(test['X'][:,:,:,i],[1,32*32*3]);
    ts_label_svhn[i,test['y'][i][0]-1]=1.0;
  ts_data_svhn=ts_data_svhn/255.0;    
  data_num_len_svhn=len(tr_label_svhn);
  
  # Get CIFAR 10  dataset
  cifar10.maybe_download_and_extract();
  tr_label_cifar10=np.zeros((50000,10),dtype=float);
  ts_label_cifar10=np.zeros((10000,10),dtype=float);
  for i in range(1,6):
    file_name=os.path.join(FLAGS.cifar_data_dir,"data_batch_"+str(i)+".bin");
    f = open(file_name,"rb");
    data=np.reshape(bytearray(f.read()),[10000,3073]);
    if(i==1):
      tr_data_cifar10=data[:,1:]/255.0;
    else:
      tr_data_cifar10=np.append(tr_data_cifar10,data[:,1:]/255.0,axis=0);
    for j in range(len(data)):
      tr_label_cifar10[(i-1)*10000+j,data[j,0]]=1.0;
  file_name=os.path.join(FLAGS.cifar_data_dir,"test_batch.bin");
  f = open(file_name,"rb");
  data=np.reshape(bytearray(f.read()),[10000,3073]);
  for i in range(len(data)):
    ts_label_cifar10[i,data[i,0]]=1.0;
  ts_data_cifar10=data[:,1:]/255.0;
  data_num_len_cifar10=len(tr_label_cifar10);
  
  tr_data1=tr_data_svhn;
  tr_label1=tr_label_svhn;
  ts_data1=ts_data_svhn;
  ts_label1=ts_label_svhn;
  data_num_len1=data_num_len_svhn;
  tr_data2=tr_data_cifar10;
  tr_label2=tr_label_cifar10;
  ts_data2=ts_data_cifar10;
  ts_label2=ts_label_cifar10;
  data_num_len2=data_num_len_cifar10;
  
  ## TASK 1 (SVHN)
  sess = tf.InteractiveSession()
  # Create a multilayer model.

  # Input placeholders
  with tf.name_scope('input'):
    x = tf.placeholder(tf.float32, [None, 32*32*3], name='x-input')
    y_ = tf.placeholder(tf.float32, [None, 10], name='y-input')

  with tf.name_scope('input_reshape'):
    image_shaped_input = tf.reshape(x, [-1, 32, 32, 3])
    tf.summary.image('input', image_shaped_input, 10)

  # geopath_examples
  geopath=pathnet.geopath_initializer(FLAGS.L,FLAGS.M);
  
  # fixed weights list
  fixed_list=np.ones((FLAGS.L,FLAGS.M),dtype=str);
  for i in range(FLAGS.L):
    for j in range(FLAGS.M):
      fixed_list[i,j]='0';    
  
  # reinitializing weights list
  rein_list=np.ones((FLAGS.L,FLAGS.M),dtype=str);
  for i in range(FLAGS.L):
    for j in range(FLAGS.M):
      rein_list[i,j]='0';    
  
  # Input Layer
  """
  input_weights=pathnet.module_weight_variable([784,FLAGS.filt]);
  input_biases=pathnet.module_bias_variable([FLAGS.filt]);
  net = pathnet.nn_layer(x,input_weights,input_biases,'input_layer');
  """

  # Hidden Layers
  weights_list=np.zeros((FLAGS.L,FLAGS.M),dtype=object);
  biases_list=np.zeros((FLAGS.L,FLAGS.M),dtype=object);
  for i in range(FLAGS.L):
    for j in range(FLAGS.M):
      if(i==0):
        weights_list[i,j]=pathnet.module_weight_variable([32*32*3,FLAGS.filt]);
        biases_list[i,j]=pathnet.module_bias_variable([FLAGS.filt]);
      else:
        weights_list[i,j]=pathnet.module_weight_variable([FLAGS.filt,FLAGS.filt]);
        biases_list[i,j]=pathnet.module_bias_variable([FLAGS.filt]);
  
  for i in range(FLAGS.L):
    layer_modules_list=np.zeros(FLAGS.M,dtype=object);
    for j in range(FLAGS.M):
      if(i==0):
        layer_modules_list[j]=pathnet.module(x, weights_list[i,j], biases_list[i,j], 'layer'+str(i+1)+"_"+str(j+1))*geopath[i,j];
      else:
        layer_modules_list[j]=pathnet.module(net, weights_list[i,j], biases_list[i,j], 'layer'+str(i+1)+"_"+str(j+1))*geopath[i,j];
    net=np.sum(layer_modules_list);
    
  """
  with tf.name_scope('dropout'):
    keep_prob = tf.placeholder(tf.float32)
    tf.summary.scalar('dropout_keep_probability', keep_prob)
    dropped = tf.nn.dropout(hidden1, keep_prob)
  """
  
  # Do not apply softmax activation yet, see below.
  output_weights=pathnet.module_weight_variable([FLAGS.filt,10]);
  output_biases=pathnet.module_bias_variable([10]);
  y = pathnet.nn_layer(net,output_weights,output_biases,'output_layer', act=tf.identity);

  with tf.name_scope('cross_entropy'):
    diff = tf.nn.softmax_cross_entropy_with_logits(labels=y_, logits=y)
    with tf.name_scope('total'):
      cross_entropy = tf.reduce_mean(diff)
  tf.summary.scalar('cross_entropy', cross_entropy)
  # Need to learn variables
  #var_list_to_learn=[]+input_weights+input_biases+output_weights+output_biases;
  var_list_to_learn=[]+output_weights+output_biases;
  for i in range(FLAGS.L):
    for j in range(FLAGS.M):
      if (fixed_list[i,j]=='0'):
        var_list_to_learn+=weights_list[i,j]+biases_list[i,j];
        
  with tf.name_scope('train'):
    train_step = tf.train.AdamOptimizer(FLAGS.learning_rate).minimize(
        cross_entropy,var_list=var_list_to_learn)
        
  def feed_dict(train,tr_flag=0):
    #Make a TensorFlow feed_dict: maps data onto Tensor placeholders.
    if train or FLAGS.fake_data:
      xs=tr_data1[tr_flag:tr_flag+16,:]; ys=tr_label1[tr_flag:tr_flag+16,:];
      k = FLAGS.dropout
    else:
      xs=ts_data1;ys=ts_label1;
      k = 1.0
    return {x: xs, y_: ys}

  with tf.name_scope('accuracy'):
    with tf.name_scope('correct_prediction'):
      correct_prediction = tf.equal(tf.argmax(y, 1), tf.argmax(y_, 1))
    with tf.name_scope('accuracy'):
      accuracy = tf.reduce_mean(tf.cast(correct_prediction, tf.float32))
  tf.summary.scalar('accuracy', accuracy)

  # Merge all the summaries and write them out to /tmp/tensorflow/mnist/logs/mnist_with_summaries (by default)
  merged = tf.summary.merge_all()
  train_writer = tf.summary.FileWriter(FLAGS.log_dir + '/train', sess.graph)
  test_writer = tf.summary.FileWriter(FLAGS.log_dir + '/test')
  tf.global_variables_initializer().run()

  # Generating randomly geopath
  geopath_set=np.zeros(FLAGS.candi,dtype=object);
  for i in range(FLAGS.candi):
    geopath_set[i]=pathnet.get_geopath(FLAGS.L,FLAGS.M,FLAGS.N);
 
  # parameters placeholders and ops 
  var_update_ops=np.zeros(len(var_list_to_learn),dtype=object);
  var_update_placeholders=np.zeros(len(var_list_to_learn),dtype=object);
  for i in range(len(var_list_to_learn)):
    var_update_placeholders[i]=tf.placeholder(var_list_to_learn[i].dtype,shape=var_list_to_learn[i].get_shape());
    var_update_ops[i]=var_list_to_learn[i].assign(var_update_placeholders[i]);
 
  # geopathes placeholders and ops 
  geopath_update_ops=np.zeros((len(geopath),len(geopath[0])),dtype=object);
  geopath_update_placeholders=np.zeros((len(geopath),len(geopath[0])),dtype=object);
  for i in range(len(geopath)):
    for j in range(len(geopath[0])):
      geopath_update_placeholders[i,j]=tf.placeholder(geopath[i,j].dtype,shape=geopath[i,j].get_shape());
      geopath_update_ops[i,j]=geopath[i,j].assign(geopath_update_placeholders[i,j]);

  tr_flag=0; 
  for i in range(FLAGS.max_steps):
    # Select Two Candidate to Tournament 
    first,second=pathnet.select_two_candi(FLAGS.candi);
    
    # First Candidate
    pathnet.geopath_insert(sess,geopath_update_placeholders,geopath_update_ops,geopath_set[first],FLAGS.L,FLAGS.M);
    var_list_backup=pathnet.parameters_backup(var_list_to_learn);
    tr_flag_bak=tr_flag;
    for j in range(FLAGS.T):
      summary_geo1_tr, _ = sess.run([merged,train_step], feed_dict=feed_dict(train=True,tr_flag=tr_flag));
      tr_flag=(tr_flag+16)%data_num_len1;
    summary_geo1_ts, acc_geo1 = sess.run([merged, accuracy], feed_dict=feed_dict(train=False));
    var_list_task1=pathnet.parameters_backup(var_list_to_learn);
    tr_flag=tr_flag_bak;
    # Second Candidate
    pathnet.geopath_insert(sess,geopath_update_placeholders,geopath_update_ops,geopath_set[second],FLAGS.L,FLAGS.M);
    pathnet.parameters_update(sess,var_update_placeholders,var_update_ops,var_list_backup);
    for j in range(FLAGS.T):
      summary_geo2_tr, _ = sess.run([merged,train_step], feed_dict=feed_dict(train=True,tr_flag=tr_flag));
      tr_flag=(tr_flag+16)%data_num_len1;
    summary_geo2_ts, acc_geo2 = sess.run([merged, accuracy], feed_dict=feed_dict(train=False));
    var_list_task2=pathnet.parameters_backup(var_list_to_learn);
    
    # Compatition between two cases
    if(acc_geo1>acc_geo2):
      geopath_set[second]=np.copy(geopath_set[first]);
      pathnet.mutation(geopath_set[second],FLAGS.L,FLAGS.M,FLAGS.N);
      pathnet.parameters_update(sess,var_update_placeholders,var_update_ops,var_list_task1);
      train_writer.add_summary(summary_geo1_tr, i);
      test_writer.add_summary(summary_geo1_ts, i);
      print('Accuracy at step %s: %s' % (i+1, acc_geo1));
    else:
      geopath_set[first]=np.copy(geopath_set[second]);
      pathnet.mutation(geopath_set[first],FLAGS.L,FLAGS.M,FLAGS.N);
      pathnet.parameters_update(sess,var_update_placeholders,var_update_ops,var_list_task2);
      train_writer.add_summary(summary_geo2_tr, i);
      test_writer.add_summary(summary_geo2_ts, i);
      print('Accuracy at step %s: %s' % (i+1, acc_geo2));
 
  if(acc_geo1>acc_geo2): 
    task1_acc=acc_geo1;
    task1_optimal_path=geopath_set[first];
  else:
    task1_acc=acc_geo2;    
    task1_optimal_path=geopath_set[second];

  # Fix task1 Optimal Path
  for i in range(FLAGS.L):
    for j in range(FLAGS.M):
      if(task1_optimal_path[i,j]==1.0):
        fixed_list[i,j]='1';

  # Get variables of fixed list
  var_list_to_fix=[]+output_weights+output_biases;
  for i in range(FLAGS.L):
    for j in range(FLAGS.M):
     if(fixed_list[i,j]=='1'):
       var_list_to_fix+=weights_list[i,j]+biases_list[i,j];
  var_list_fix=pathnet.parameters_backup(var_list_to_fix);

  # parameters placeholders and ops
  var_fix_ops=np.zeros(len(var_list_to_fix),dtype=object);
  var_fix_placeholders=np.zeros(len(var_list_to_fix),dtype=object);
  for i in range(len(var_list_to_fix)):
    var_fix_placeholders[i]=tf.placeholder(var_list_to_fix[i].dtype,shape=var_list_to_fix[i].get_shape());
    var_fix_ops[i]=var_list_to_fix[i].assign(var_fix_placeholders[i]);

 
  ## TASK 2 (CIFAR 10) 
  # Output Layer for Task2
  output_weights2=pathnet.module_weight_variable([FLAGS.filt,10]);
  output_biases2=pathnet.module_bias_variable([10]);
  y2 = pathnet.nn_layer(net,output_weights2,output_biases2,'output_layer2', act=tf.identity);  

  with tf.name_scope('cross_entropy2'):
    diff2 = tf.nn.softmax_cross_entropy_with_logits(labels=y_, logits=y2)
    with tf.name_scope('total2'):
      cross_entropy2 = tf.reduce_mean(diff2)
  tf.summary.scalar('cross_entropy2', cross_entropy2)
  
  # Need to learn variables
  #var_list_to_learn=[]+input_weights+input_biases+output_weights2+output_biases2;
  var_list_to_learn=[]+output_weights2+output_biases2;
  for i in range(FLAGS.L):
    for j in range(FLAGS.M):
      if (fixed_list[i,j]=='0'):
        var_list_to_learn+=weights_list[i,j]+biases_list[i,j];
        
  with tf.name_scope('train2'):
    train_step2 = tf.train.AdamOptimizer(FLAGS.learning_rate).minimize(
        cross_entropy2,var_list=var_list_to_learn)  
    #train_step2 = tf.train.GradientDescentOptimizer(FLAGS.learning_rate).minimize(
    #    cross_entropy2,var_list=var_list_to_learn)  
  
  with tf.name_scope('accuracy2'):
    with tf.name_scope('correct_prediction2'):
      correct_prediction2 = tf.equal(tf.argmax(y2, 1), tf.argmax(y_, 1))
    with tf.name_scope('accuracy2'):
      accuracy2 = tf.reduce_mean(tf.cast(correct_prediction2, tf.float32))
  tf.summary.scalar('accuracy2', accuracy2)

  # Merge all the summaries and write them out to /tmp/tensorflow/mnist/logs/mnist_with_summaries (by default)
  merged2 = tf.summary.merge_all()
  train_writer = tf.summary.FileWriter(FLAGS.log_dir + '/train2', sess.graph)
  test_writer = tf.summary.FileWriter(FLAGS.log_dir + '/test2')
  tf.global_variables_initializer().run()

  # Update fixed values
  pathnet.parameters_update(sess,var_fix_placeholders,var_fix_ops,var_list_fix);

  def feed_dict2(train,tr_flag=0):
    #Make a TensorFlow feed_dict: maps data onto Tensor placeholders.
    if train or FLAGS.fake_data:
      xs=tr_data2[tr_flag:tr_flag+16,:]; ys=tr_label2[tr_flag:tr_flag+16,:];
      k = FLAGS.dropout
    else:
      xs=ts_data2;ys=ts_label2;
      k = 1.0
    return {x: xs, y_: ys}
  
  # Generating randomly geopath
  geopath_set=np.zeros(FLAGS.candi,dtype=object);
  for i in range(FLAGS.candi):
    geopath_set[i]=pathnet.get_geopath(FLAGS.L,FLAGS.M,FLAGS.N);

  # parameters placeholders and ops 
  var_update_ops=np.zeros(len(var_list_to_learn),dtype=object);
  var_update_placeholders=np.zeros(len(var_list_to_learn),dtype=object);
  for i in range(len(var_list_to_learn)):
    var_update_placeholders[i]=tf.placeholder(var_list_to_learn[i].dtype,shape=var_list_to_learn[i].get_shape());
    var_update_ops[i]=var_list_to_learn[i].assign(var_update_placeholders[i]);
    
  tr_flag=0;
  for i in range(FLAGS.max_steps):
    # Select Two Candidate to Tournament 
    first,second=pathnet.select_two_candi(FLAGS.candi);
    
    # First Candidate
    pathnet.geopath_insert(sess,geopath_update_placeholders,geopath_update_ops,geopath_set[first],FLAGS.L,FLAGS.M);
    tr_flag_bak=tr_flag;
    var_list_backup=pathnet.parameters_backup(var_list_to_learn);
    for j in range(FLAGS.T):
      summary_geo1_tr, _ = sess.run([merged2, train_step2], feed_dict=feed_dict2(True,tr_flag))
      tr_flag=(tr_flag+16)%data_num_len2;
    summary_geo1_ts, acc_geo1 = sess.run([merged2, accuracy2], feed_dict=feed_dict2(False))
    var_list_task1=pathnet.parameters_backup(var_list_to_learn);
    
    # Second Candidate
    pathnet.geopath_insert(sess,geopath_update_placeholders,geopath_update_ops,geopath_set[first],FLAGS.L,FLAGS.M);
    tr_flag=tr_flag_bak;
    pathnet.parameters_update(sess,var_update_placeholders,var_update_ops,var_list_backup);
    for j in range(FLAGS.T-1):
      summary_geo2_tr, _, acc_geo2_tmp = sess.run([merged2, train_step2,accuracy2], feed_dict=feed_dict2(True,tr_flag))
      tr_flag=(tr_flag+16)%data_num_len2;
    summary_geo2_ts, acc_geo2 = sess.run([merged2, accuracy2], feed_dict=feed_dict2(False))
    var_list_task2=pathnet.parameters_backup(var_list_to_learn);
    
    # Compatition between two cases
    if(acc_geo1>acc_geo2):
      geopath_set[second]=np.copy(geopath_set[first]);
      pathnet.mutation(geopath_set[second],FLAGS.L,FLAGS.M,FLAGS.N);
      pathnet.parameters_update(sess,var_update_placeholders,var_update_ops,var_list_task1);
      train_writer.add_summary(summary_geo1_tr, i);
      test_writer.add_summary(summary_geo1_ts, i);
      print('Accuracy at step %s: %s' % (i+1, acc_geo1));
    else:
      geopath_set[first]=np.copy(geopath_set[second]);
      pathnet.mutation(geopath_set[first],FLAGS.L,FLAGS.M,FLAGS.N);
      pathnet.parameters_update(sess,var_update_placeholders,var_update_ops,var_list_task2);
      train_writer.add_summary(summary_geo2_tr, i);
      test_writer.add_summary(summary_geo2_ts, i);
      print('Accuracy at step %s: %s' % (i+1, acc_geo2));
  
  if(acc_geo1>acc_geo2): 
    task2_acc=acc_geo1;
  else:
    task2_acc=acc_geo2;        
  print("SVHN Acc:"+str(task1_acc)+",CIFAR10:"+str(task2_acc));
  
  train_writer.close()
  test_writer.close()

def main(_):
  if tf.gfile.Exists(FLAGS.log_dir):
    tf.gfile.DeleteRecursively(FLAGS.log_dir)
  tf.gfile.MakeDirs(FLAGS.log_dir)
  train()


if __name__ == '__main__':
  parser = argparse.ArgumentParser()
  parser.add_argument('--fake_data', nargs='?', const=True, type=bool,
                      default=False,
                      help='If true, uses fake data for unit testing.')
  parser.add_argument('--learning_rate', type=float, default=0.001,
                      help='Initial learning rate')
  parser.add_argument('--max_steps', type=int, default=500,
                      help='Number of steps to run trainer.')
  parser.add_argument('--dropout', type=float, default=0.9,
                      help='Keep probability for training dropout.')
  parser.add_argument('--cifar_data_dir', type=str, default='/tmp/cifar10_data/cifar-10-batches-bin',
                      help='Directory for storing input data')
  parser.add_argument('--svhn_data_dir', type=str, default='/tmp/svhn_dataset',
                      help='Directory for storing input data')
  parser.add_argument('--log_dir', type=str, default='/tmp/tensorflow/pathnet/logs/svhn_cifar10',
                      help='Summaries log directory')
  parser.add_argument('--M', type=int, default=10,
                      help='The Number of Modules per Layer')
  parser.add_argument('--L', type=int, default=3,
                      help='The Number of Layers')
  parser.add_argument('--N', type=int, default=4,
                      help='The Number of Selected Modules per Layer')
  parser.add_argument('--T', type=int, default=50,
                      help='The Number of epoch per each geopath')
  parser.add_argument('--filt', type=int, default=20,
                      help='The Number of Filters per Module')
  parser.add_argument('--candi', type=int, default=64,
                      help='The Number of Candidates of geopath')
  FLAGS, unparsed = parser.parse_known_args()
  tf.app.run(main=main, argv=[sys.argv[0]] + unparsed)
