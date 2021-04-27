class ParameterManager{
    constructor() {
      // Stimulus parameters
      this.repetition = 0;
      this.ind_stimcond = 0;
      this.flag_block = false;

      this.num_rep =num_rep_main;
  
      // Results parameters;
      this.tmp_res_ob = 0;
      this.tmp_rt = null;
      this.results_responses = [];
      this.results_rt = [];
      this.results_ind_switch = [];
      this.results_taskcond = [];
      this.results_colorcond = [];
      this.results_shapecond = [];
      this.initialize();
    }

    initialize(){
      // condition setting
      this.ind_switch = [];      
      this.trial_target = shuffle(array_target);
      for (let i=0;i<this.num_rep;i++){
        this.ind_switch = concat(this.ind_switch,array_stimcond);
      }
      this.ind_switch = shuffle(this.ind_switch);
  
      this.ind_task = shuffle([0,1]); 
      this.ind_task = int(this.ind_task[0]); //initialize the first task;
  
      this.taskcond = array_taskcond;
      this.colorcond = shuffle(array_colorcond);
      this.shapecond = shuffle(array_shapecond);
      if (this.colorcond[0]==0){
        this.color = col_0;
      } else{
        this.color = col_1;
      }
    }
    
    next_trial(){
      this.save(); //This task saves the data once per block.
  
      //set the next trial parameters
      this.set_stimlusorder_trial();
      this.ind_stimcond ++;
      this.tmp_res_ob = 0;
      this.tmp_rt = null;
      if (this.ind_stimcond==this.ind_switch.length){
        this.flag_block = true;
      }
    }
  
    next_block(){
      //in this experiment, this function is just for the save of the last trial.
      //The last value of the ind_switch is the same as the one before just for pudding.
      this.ind_stimcond = this.ind_stimcond-1;
      this.save(); 
    }
  
    set_stimlusorder_trial(){
      if (this.ind_switch[this.ind_stimcond]==1){
        this.ind_task = Math.abs(this.ind_task -1);
      }
      this.trial_target = shuffle(array_target);
      this.colorcond = shuffle(array_colorcond);
      this.shapecond = shuffle(array_shapecond);
      if (this.colorcond[0]==0){
        this.color = col_0;
      } else{
        this.color = col_1;
      }
    }
  
  
    save(){
      // store the current stimulus and response data to the result dictionary.
      this.results_responses.push(this.tmp_res_ob);
      this.results_rt.push(this.tmp_rt);
      this.results_ind_switch.push(this.ind_switch[this.ind_stimcond]);
      this.results_taskcond.push(this.taskcond[this.ind_task]);
      this.results_colorcond.push(this.colorcond[0]);
      this.results_shapecond.push(this.shapecond[0]);
    }
  }
  
  