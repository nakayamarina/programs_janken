PATH_DATA="../../Data_mri/jankenState-2fe/"
PATH_SAVE="../"

for dir in 20181029rn 20181029su 20181029tm
do

  for image_method in 64ch mb
  do

    PATH_NII="${PATH_DATA}${dir}/${image_method}/"


    PATH_BA="${PATH_SAVE}State-2fe_MaskBrodmann/${dir}/${image_method}/"

    echo "------------ ${PATH_NII} | ${PATH_BA} ---------------"

    python Preprocessing_nii2zscore.py ${PATH_NII} ${PATH_BA} rwmaskBA.nii



    PATH_MOTOR="${PATH_SAVE}State-2fe_MaskMotor/${dir}/${image_method}/"

    echo "------------ ${PATH_NII} | ${PATH_MOTOR} ---------------"

    python Preprocessing_nii2zscore.py ${PATH_NII} ${PATH_MOTOR} rwmask12346.nii

  done


done
