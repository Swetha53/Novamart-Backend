package com.novamart.payment_service.respository;

import com.novamart.payment_service.model.Payment;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;

import java.util.List;

public interface PaymentRepository extends JpaRepository<Payment, String> {
   @Query("SELECT p FROM Payment p WHERE p.orderId = ?1")
   List<Payment> findByOrderId(String orderId);
}
